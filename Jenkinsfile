pipeline {
    // Run on any available Jenkins agent
    agent any

    // Define environment variables
    environment {
        // --- THIS IS THE SECTION YOU MUST EDIT ---
        
        // 1. The name of your Elastic Beanstalk Application
        //    (This MUST match what you just created: 'flask-todo-api')
        APP_NAME         = 'flask-todo-api'
        
        // 2. The name of the Environment to deploy to
        //    (This MUST match what you just created: 'Flask-todo-api-env')
        ENV_NAME         = 'flask-todo-api-prod' 
        
        // 3. The S3 bucket you created for the build zips
        //    (This is your 'jenkins-build-artifacts-aj')
        S3_BUCKET        = 'jenkins-build-artifacts-aj' 
        
        // 4. The AWS region for all commands
        AWS_REGION       = 'ap-south-1'
        
        // 5. Your FULL RDS Database URL (as a secret)
        //    (This ID MUST match the one you created in Jenkins: 'RDS_DATABASE_URL')
        DATABASE_URL     = credentials('RDS_DATABASE_URL')
        
        // --- END OF SECTION TO EDIT ---
        
        // This makes sure the 'aws' and 'eb' commands are found,
        // using the new pipx path.
        PATH             = "/var/lib/jenkins/.local/bin:${env.PATH}"
        
        // We'll use the build number to create unique version labels
        ZIP_FILE_NAME    = "backend-build-${BUILD_NUMBER}.zip"
        VERSION_LABEL    = "backend-build-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Install Python Dependencies') {
            steps {
                echo 'Creating venv and installing requirements...'
                // 1. Create the virtual environment
                sh 'python3 -m venv venv'
                
                // 2. Use the pip *inside* the venv to install packages
                //    This is the CORRECTED line. No 'source' needed.
                sh 'venv/bin/pip install -r requirements.txt'
            }
        }
        
        stage('Migrate Database') {
            steps {
                echo 'Running database migrations...'
                // 1. Use the python *inside* the venv to run the script
                //    This is the CORRECTED line. No 'source' needed.
                sh 'venv/bin/python run_migrations.py'
            }
        }

        stage('Create Application Zip') {
            steps {
                echo 'Creating application zip file...'
                sh '''
                    zip -r ${ZIP_FILE_NAME} . \
                        -x ".git/*" \
                        -x ".gitignore" \
                        -x "Jenkinsfile" \
                        -x ".ebextensions/*" \
                        -x "venv/*" \
                        -x "__pycache__/*" \
                        -x "*.db" \
                        -x ".env"
                '''
            }
        }

        stage('Upload to S3 Artifact Bucket') {
            steps {
                echo 'Uploading zip to S3...'
                sh 'aws s3 cp ${ZIP_FILE_NAME} s3://${S3_BUCKET}/${ZIP_FILE_NAME} --region ${AWS_REGION}'
            }
        }

        stage('Create New Application Version') {
            steps {
                echo 'Creating new application version in Elastic Beanstalk...'
                sh '''
                    aws elasticbeanstalk create-application-version \
                        --application-name ${APP_NAME} \
                        --version-label ${VERSION_LABEL} \
                        --source-bundle S3Bucket=${S3_BUCKET},S3Key=${ZIP_FILE_NAME} \
                        --region ${AWS_REGION} \
                        --auto-create-application
                '''
            }
        }

        stage('Deploy to Environment') {
            steps {
                echo 'Deploying new version to environment...'
                sh '''
                    aws elasticbeanstalk update-environment \
                        --application-name ${APP_NAME} \
                        --environment-name ${ENV_NAME} \
                        --version-label ${VERSION_LABEL} \
                        --region ${AWS_REGION}
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace...'
            deleteDir() // Deletes the zip file and checked-out code
        }
    }
}