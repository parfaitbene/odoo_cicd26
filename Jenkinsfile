pipeline {
    agent {
        node {
            label "lab-odoo.parfaitbene.com"
        }
    }

    environment {
        DOCKER_CONTAINER_NAME_PREFIX = "odoo_web"
    }

    stages {

        stage("Build") {
            steps {
                echo "Building docker images..."
                sh "cp /app_odoo/odoo_pg_pass ./"
                sh "mkdir -p ./config"
                sh "cp -r /app_odoo/config/odoo.conf ./config/odoo.conf"
                sh "docker compose -f ./docker/docker-compose.yml build"
            }
        }

        stage("Modules Update") {
            steps {
                echo "Odoo Modules Update..."
                sh "docker compose -f ./docker/docker-compose.yml down"
                sh '''
                    docker compose -f ./docker/docker-compose.yml run --rm --remove-orphans odoo_web odoo --update=$(cat ./modules.txt | tr '\n' ',') --stop-after-init
                '''
                sh '''
                    docker stop $(docker ps --filter name=${DOCKER_CONTAINER_NAME_PREFIX} -q) || true
                '''
            }
        }

        stage("Deploy") {
            steps {
                echo "Starting the application..."
                sh "docker compose -f ./docker/docker-compose.yml up -d"
            }
        }
    }

    post {
        always {
            sh "docker system prune -f"
        }
        success {
            echo 'Déploiement réussi !'
        }
        failure {
            echo 'Échec du déploiement.'
        }
    }
}
