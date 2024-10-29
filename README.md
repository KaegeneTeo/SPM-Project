# SPM-Project

[![codecov](https://codecov.io/github/bokiex/SPM-Project/branch/dev/graph/badge.svg?token=GP2GB88CHB)](https://codecov.io/github/bokiex/SPM-Project) <-- Unit test code coverage for /backend folder.

Aiowa is short for All In One Work Arrangement web app. It's a HRMS system that allows employees to apply for work schedule and directors and HR to approve them.

Frontend is VueJS hosted on Vercel and backend is done with Zappa, a python library that creates serverless Python applications. Python Flask is hosted on AWS Lambda using Zappa.

To run frontend locally:

```
# cd into /aiowa folder
npm install
npm run dev
```

A .env file with the backend URL needs to be placed in /aiowa folder

```
export VITE_AWS_URL=https://xkq7fx1ej1.execute-api.ap-southeast-1.amazonaws.com/dev
```

Not recommended to run backend locally because it connects to Supabase and we cannot provide the key here.

Development environment link: https://spm-project-dev.vercel.app

Production environment link: https://spm-project-five.vercel.app/
