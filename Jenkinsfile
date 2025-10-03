pipeline {
  agent any

  environment {
    GIT_REPO = 'https://github.com/Tanvi-source/3-tier-architecture.git'
    DOCKER_HOST = '3.110.209.85'   // replace with your docker server IP/hostname (or configure as Jenkins param)
    DOCKER_REPO = 'tanvibhusari/3tier'   // replace
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & run on Docker server') {
      steps {
        sshagent (credentials: ['docker-host-ssh']) {
          // run a remote script that pulls the repo, builds images and runs containers
          sh """
            ssh -o StrictHostKeyChecking=no ubuntu@${DOCKER_HOST} '
              set -e
              mkdir -p /opt/3-tier-docker
              if [ -d /opt/3-tier-docker/.git ]; then
                cd /opt/3-tier-docker
                git fetch --all
                git reset --hard origin/main
              else
                rm -rf /opt/3-tier-docker
                git clone ${GIT_REPO} /opt/3-tier-docker
                cd /opt/3-tier-docker
              fi
              # ensure docker-compose is present on server
              cd /opt/3-tier-docker
              # Build images and bring up containers (db, backend, nginx)
              docker-compose build --no-cache
              docker-compose up -d db backend nginx
            '
          """
        }
      }
    }

    stage('Smoke test') {
      steps {
        echo "Waiting 10s for services..."
        sh 'sleep 10'
        // try hitting nginx on the docker server (exposed on port 80)
        sh "curl -f http://${DOCKER_HOST} || (echo 'Smoke test failed' && exit 1)"
      }
    }

    stage('Push images & Deploy to Kubernetes (Ansible)') {
      steps {
        // get DockerHub creds from Jenkins credential store (id: dockerhub-creds)
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          // Run ansible-playbook (assumes ansible is installed on the Jenkins node)
          sh """
            ansible-playbook ansible/push_and_deploy.yml -i ansible/inventory.ini \
              --extra-vars "docker_host=${DOCKER_HOST} docker_repo=${DOCKER_REPO} image_tag=${IMAGE_TAG} docker_user=${DH_USER} docker_pass=${DH_PASS}"
          """
        }
      }
    }
  }

  post {
    failure {
      echo 'Pipeline failed. Check logs.'
    }
    success {
      echo 'Done — pushed images and deployed to Kubernetes.'
    }
  }
}
