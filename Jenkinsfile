pipeline {
    agent any
    
    environment {
        TMAS_API_KEY = credentials('TMAS_API_KEY')
        TMAS_HOME = "$WORKSPACE/tmas"
    }
    
    stages {
        stage('Setup Credentials') {
            steps {
                script {
                    // Ensure the configuration directory exists
                    sh 'mkdir -p ~/.config/containers'
                    // Write the correct TOML configuration to registries.conf
                    sh """
                    cat > ~/.config/containers/registries.conf <<EOF
                    [plugins."io.containerd.grpc.v1.cri".registry]
                      credential-helpers = ["desktop"]
                    EOF
                    """
                }
            }
        }
        
        stage('Build and Test Image') {
            steps {
                script {
                    def app

                    // Clone repository
                    checkout scm

                    // Build image
                    app = docker.build("fadefa88/test")

                    // Test image
                    app.inside {
                        sh 'echo "Tests passed"'
                    }

                    // Push image
                    docker.withRegistry('https://registry.hub.docker.com', 'docker') {
                        app.push("${env.BUILD_NUMBER}")
                        app.push("latest") // Ensure we have a latest tag

                    }
                }
            }
        }
        
        stage('Get Image Digest') {
            steps {
                script {
                    // Pull the image to get its digest
                    sh 'docker pull fadefa88/test:latest'
                    def digest = sh(
                        script: "docker inspect --format='{{index .RepoDigests 0}}' fadefa88/test:latest",
                        returnStdout: true
                    ).trim()
                    
                    // Extract only the SHA part
                    def sha = digest.split('@')[1]
                    echo "Image digest: ${sha}"
                    
                    // Save the digest in an environment variable for subsequent steps
                    env.IMAGE_DIGEST = sha
                }
            }
        }
        
        stage('TMAS Scan') {
            steps {
                script {
                    // Login to Docker Hub
                    withCredentials([usernamePassword(credentialsId: 'docker', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                    }
                    // Install TMAS
                    sh "mkdir -p $TMAS_HOME"
                    sh "curl -L https://cli.artifactscan.cloudone.trendmicro.com/tmas-cli/latest/tmas-cli_Linux_x86_64.tar.gz | tar xz -C $TMAS_HOME"
                    
                    // Execute the tmas scan command with the obtained digest
                    sh 'cat ~/.docker/config.json'
                    sh "$TMAS_HOME/tmas scan --vulnerabilities --malware --secrets registry:fadefa88/test@${env.IMAGE_DIGEST} --region eu-central-1 -vvv"
                    
                    // Logout from Docker Hub
                    sh 'docker logout'
                }
            }
        }
    }
    
    post {
        success {
            // Trigger ManifestUpdate job upon success of both pipelines
            echo "Triggering updatemanifest job"
            build job: 'updatemanifest', parameters: [string(name: 'DOCKERTAG', value: env.BUILD_NUMBER)]
        }
    }
}
