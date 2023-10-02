Table of contents
=================

   * [Create Slack App](#Create-Slack-App)
   * [Add the Slack App to your desired channel](#Add-the-Slack-App-to-your-desired-channel)
   * [Build up the Docker image](#Build-up-the-Docker-image)
   * [Google Service Account](#Google-Service-Account)
     * [Initialization](#Initialization)
     * [Create service account](#Create-service-account)
     * [Create role](#Create-role)
     * [Bind service account to role](#Bind-service-account-to-role)
     * [Update the role](#Update-the-role)
     * [Describe the role](#Describe-the-role)
     * [Create Json key for the service account](#Create-Json-key-for-the-service-account)
   * [Reference](#Reference)

Create Slack App
============
1. Login to your Slack App [here](https://api.slack.com/apps/<LOGIN ID>)
2. Create a new App [here](https://api.slack.com/apps?new_app=1)
3. Choose `From Scratch`
4. Give App Name: `Slack-AI-Tool`
5. Pick up your workspace
6. Create the App
7. Go to `OAuth & Permissions`
8. Go to `Scopes`
9. Add an `OAuth Scope`: chat:write, channels:history, groups:history, mpim:history, im:history, users:read
10. Scroll up to `OAuth Token for Your Workspace` and press `Install to Workspace`
11. Copy the `Bot User OAuth Token`


Add the Slack App to your desired channel
============
1. Go to Slack
2. Pick a channel
3. Go to Channel Settings
4. Go to Integrations
5. Add apps
6. Add your Slack-AI-Tool


Google Service Account
============

Initialization
-----
```bash
export service_account_name="slack-ai"
export role_name="slack_ai"
export project_id="<project_id>"
export title="Slack AI"
```
Create service account
-----
```bash
gcloud iam service-accounts create $service_account_name --display-name "$service_account_name"
```

Create role
-----
```bash
gcloud iam roles create $role_name \
    --project $project_id \
    --title "$title" \
    --description "This role has only the necessary permissions for DevOps AI tools" \
    --permissions aiplatform.endpoints.predict
```

Bind service account to role
-----
```bash
gcloud projects add-iam-policy-binding $project_id --member 'serviceAccount:<Service Account ID>@$project_id.iam.gserviceaccount.com' --role='projects/$project_id/roles/$role_name'
```

Update the role
-----
```bash
gcloud iam roles update $role_name --project=$project_id --permissions=bigquery.jobs.create,aiplatform.endpoints.predict
```

Describe the role
-----
```bash
gcloud iam roles describe --project=$project_id $role_name
```

Create Json key for the service account
-----
```bash
gcloud iam service-accounts keys create $role_name \
    --iam-account=<Service Account ID>@$project_id.iam.gserviceaccount.com
```


Build up the Docker image
============
```bash
docker build --platform linux/amd64 -t naturalett/slack-ai:slack-ai-v1 .
```

Reference
============
1. [Link 1](https://medium.com/@kohei.nishitani/slack-chatbot-development-with-openai-an-easy-guide-for-beginners-f718d2e2c78b)