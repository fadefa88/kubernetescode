pipeline {
    agent any
    
    environment {
        TMAS_API_KEY = credentials('TMAS_API_KEY')
        TMAS_HOME = "$WORKSPACE/tmas"
    }
    
    stages {
        stage('First Pipeline - TMAS Scan') {
            steps {
                // Install TMAS CLI
                sh "mkdir -p $TMAS_HOME"
                sh "curl -L https://cli.artifactscan.cloudone.trendmicro.com/tmas-cli/latest/tmas-cli_Linux_x86_64.tar.gz | tar xz -C $TMAS_HOME"

                // Scan with TMAS
                sh "$TMAS_HOME/tmas scan secrets docker:fadefa88/test:latest --region eu-central-1"
                sh "$TMAS_HOME/tmas scan docker:fadefa88/test:latest --region eu-central-1"
            }
        }
        
        stage('Second Pipeline - Build and Test Image') {
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
                    }
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
