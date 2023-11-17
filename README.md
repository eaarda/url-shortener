
# URL SHORTENER

![PyPI - Python Version](https://img.shields.io/badge/python-3.9.6-blue
)

This project, developed using FastAPI, serves as an efficient solution for shortening lengthy URLs. 
URL Shortener is a powerful tool designed to simplify and enhance the management of long URLs. Beyond basic URL shortening, this project provides advanced features such as user accounts, URL history tracking, and comprehensive click statistics.








## Tech Stack

**Server:** FastAPI

**Database:** PostgreSQL

**Caching:** Redis

## Run Locally
Follow these steps to set up the project:


1- Clone the project
```bash
  git clone https://github.com/eaarda/url-shortener
```
2- Go to the project directory
```bash
  cd url-shortener
```
3- Install Virtual Environment First
```bash
$  pip install virtualenv
```
4- Create Virtual Environment
```bash
$  virtualenv venv
```
5- Activate Virtual Environment
```bash
$  source venv/bin/activate
```
6- Install dependencies
```bash
  pip install -r requirements.txt
```
7- Start the server after `.env` configuration

```bash
  uvicorn main:app --reload
```



## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file. Create a copy of the `.env.example` file and replace the placeholder values with your specific configuration.
### Documentation


```http
  GET /api/v1/docs
  GET /api/v1/redoc
```



## Running Tests

To run tests, run the following command

```bash
  pytest
```


## API Reference

### Shorten URL

```http
POST /api/v1/shorten
Authorization: Bearer {your_token}
```

Request Body
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `original_url` | `string` | **Required**. The original URL to be shortened|

Headers
| Header | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Authorization` | `string` | HTTP Bearer Token (optional but recommended)|

Example Request
```
curl -X POST \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/long-url-to-be-shortened"}' \
  http://your-api-base-url/api/v1/shorten

```

Example Response
```json
{
  "original_url": "https://www.example.com/long-url-to-be-shortened",
  "short_url": "https://short.url/abc123e",
  "created_at": "2023-11-17T12:00:00Z",
  "short_id": "abc123e",
  "total_clicks": 0
}
```

### Redirect Shortened URL

```http
GET /{short_id}
```

Parameters
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `short_id` | `string` | **Required**. The short ID for the original URL|

Example Request
```
curl -X 'GET' \
  -H 'accept: application/json'
  'http://your-api-base-url/abc123' \
  
```


