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
                    sh 'mkdir -p ~/.config/containers'
                    sh 'echo \'[plugins."io.containerd.grpc.v1.cri".registry]\' > ~/.config/containers/registries.conf'
                    sh 'echo \'  credential-helpers = ["desktop"]\' >> ~/.config/containers/registries.conf'
                 
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
                    // Ottieni il digest dell'immagine
                    sh 'docker pull fadefa88/test:latest'
                    def digest = sh(
                        script: "docker inspect --format='{{index .RepoDigests 0}}' fadefa88/test:latest",
                        returnStdout: true
                    ).trim()
                    
                    // Estrai solo la parte SHA
                    def sha = digest.split('@')[1]
                    echo "Image digest: ${sha}"
                    
                    // Salva il digest in una variabile d'ambiente per i passaggi successivi
                    env.IMAGE_DIGEST = sha
                }
            }
        }
        stage('TMAS Scan') {
            steps {
                script {
                    // Effettua il login a Docker Hub
                    withCredentials([usernamePassword(credentialsId: 'docker', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                    }
                    // Install TMAS
                    sh "mkdir -p $TMAS_HOME"
                    sh "curl -L https://cli.artifactscan.cloudone.trendmicro.com/tmas-cli/latest/tmas-cli_Linux_x86_64.tar.gz | tar xz -C $TMAS_HOME"
                    
                    // Esegui il comando tmas scan con il digest ottenuto
                    sh 'cat ~/.docker/config.json'
                    sh "$TMAS_HOME/tmas scan --vulnerabilities --malware --secrets registry:fadefa88/test@${env.IMAGE_DIGEST} --region eu-central-1 -vvv"
                    
                    // Effettua il logout da Docker Hub
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
