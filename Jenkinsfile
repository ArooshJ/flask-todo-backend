pipeline {
    // Run on any available Jenkins agent
    agent any

    // Define environment variables
    environment {
        // --- THIS IS THE SECTION YOU MUST EDIT ---
        
        // 1. The name of your Elastic Beanstalk Application
        //    (e.g., 'flask-todo-api')
        APP_NAME         = 'flask-todo-api'
        
        // 2. The name of the Environment to deploy to
        //    (e.g., 'Flask-todo-api-env')
        ENV_NAME         = 'Flask-todo-api-env' 
        
        // 3. The S3 bucket you JUST created for the build zips
        //    (This is your 'jenkins-build-artifacts-aj')
        S3_BUCKET        = 'jenkins-build-artifacts-aj' 
        
        // 4. The AWS region for all commands
        AWS_REGION       = 'ap-south-1'
        
        // 5. Your FULL RDS Database URL (as a secret)
        //    This ID must match the one in Jenkins Credentials
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
                // Pulls the code from your GitHub repo
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Install Python Dependencies') {
            steps {
                // Create a virtual environment and install packages
                // This is needed for the migration step
                echo 'Creating venv and installing requirements...'
                sh 'python3 -m venv venv'
                sh 'source venv/bin/activate && pip install -r requirements.txt'
            }
        }
        
        stage('Migrate Database') {
            steps {
                // Run the migration script directly from Jenkins
                // This uses the DATABASE_URL secret
                echo 'Running database migrations...'
                sh 'source venv/bin/activate && python run_migrations.py'
            }
        }

        stage('Create Application Zip') {
            steps {
                // Creates a clean zip file, excluding all the junk
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
                // Uploads the zip file to your private S3 bucket
                echo 'Uploading zip to S3...'
                sh 'aws s3 cp ${ZIP_FILE_NAME} s3://${S3_BUCKET}/${ZIP_FILE_NAME} --region ${AWS_REGION}'
            }
        }

        stage('Create New Application Version') {
            steps {
                // Tells Elastic Beanstalk about the new S3 zip file
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
                // Tells your environment to update itself with the new version
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
        // This 'post' block runs after all stages
        always {
            // Clean up the workspace
            echo 'Cleaning up workspace...'
            deleteDir() // Deletes the zip file and checked-out code
        }
    }
}