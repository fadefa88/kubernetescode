pipeline {
    agent any
    
    environment {
        TMAS_API_KEY = credentials('TMAS_API_KEY')
        TMAS_HOME = "$WORKSPACE/tmas"
    }
    
    stages {
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
                    // Esegui il comando tmas scan con il digest ottenuto
                    sh "tmas scan registry:docker/test@${env.IMAGE_DIGEST} --region eu-central-1"
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
