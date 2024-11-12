# ICETEX Scholarship Notifier

This project performs **web scraping** on the ICETEX scholarship page, stores the data in **Firebase**, and notifies about new scholarships via **Telegram** and **configurable webhooks**.

## Features

- **Web Scraping**: Extracts scholarship information from the ICETEX website.
- **Firebase**: Stores scraped scholarships and verifies if they are new.
- **Notifications**:
  - **Telegram**: Sends notifications to a specified group or user.
  - **Webhooks**: Sends data to user-defined endpoints.
- **Automation**: Configurable via cron jobs to execute daily at 9:00 a.m.

---

## Project Structure

```
icetex-scholarship-notifier/
├── configs/
│   ├── firebase.json         # Firebase configuration
│   ├── webhooks.json         # Webhooks configuration
├── src/
│   ├── config.py
│   ├── firebase.py
│   ├── main.py
│   ├── notifications.py
│   ├── scraper.py
├── cronjob
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Prerequisites

1. **Python 3.9+**
2. **Docker (Optional)**: To run in a containerized environment.
3. Required environment variables:

   - `TELEGRAM_BOT_TOKEN`: Telegram bot token.
   - `TELEGRAM_CHAT_ID`: Telegram chat ID (group or user).

4. JSON files:
   - `configs/firebase.json`: Firebase project credentials.
   - `configs/webhooks.json`: List of configured webhooks.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/icetex-scholarship-notifier.git
cd icetex-scholarship-notifier
```

### 2. Install Dependencies

Make sure to activate a virtual environment:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Add JSON Files

Place `firebase.json` and `webhooks.json` inside the `configs/` directory.

- **firebase.json**:
  Credentials generated from the Firebase console.

- **webhooks.json**:
  Example:
  ```json
  [
    {
      "url": "https://example-webhook-url.com/notify",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN"
      },
      "message_body_key": "text",
      "additional_body": {
        "priority": "high",
        "type": "scholarship_notification"
      }
    }
  ]
  ```

#### Webhook Configuration

The `webhooks.json` file defines how the project sends data to external endpoints. Each webhook should be an object with the following properties:

#### Properties

- **`url`**: The endpoint to send the data.
- **`method`**: HTTP method to use (e.g., `POST`, `PUT`).
- **`headers`**: Optional. HTTP headers required by the webhook.
- **`message_body_key`**: The key in the request body where the scholarship message will be inserted.
  - For example, if `message_body_key` is `"text"`, the request body will look like this:
    ```json
    {
      "text": "🎓 New Scholarship Available!",
      "priority": "high",
      "type": "scholarship_notification"
    }
    ```
- **`additional_body`**: Optional. Additional data to include in the body of the request.

---

## Usage

### Run Locally

```bash
python src/main.py
```

### Run with Docker

#### 1. Build the Image

```bash
docker build -t icetex-scholarship-notifier .
```

#### 2. Run the Container

You can specify individual JSON files or the entire directory. For individual files, use the following:

```bash
docker run -d \
  --name icetex-scholarship-notifier \
  --env TELEGRAM_BOT_TOKEN=your_bot_token \
  --env TELEGRAM_CHAT_ID=your_chat_id \
  -v $(pwd)/configs/firebase.json:/app/configs/firebase.json:ro \
  -v $(pwd)/configs/webhooks.json:/app/configs/webhooks.json:ro \
  icetex-scholarship-notifier
```

> **Notes**:
>
> - You can mount the entire `configs/` folder if preferred:
>   ```bash
>   -v $(pwd)/configs:/app/configs:ro
>   ```
> - The `:ro` flag ensures the JSON files are mounted as read-only for added security.

---

## Automation with Cron Jobs

The project includes a configuration to run the script automatically at 9:00 a.m. daily. This can be set up using a cron job on the operating system or by running the Docker container with an orchestration tool like Kubernetes.

Example cron job for a local server:

```bash
0 9 * * * cd /path/to/icetex-scholarship-notifier && python src/main.py
```

---

## Contributing

1. Fork the repository.
2. Create a branch for your feature:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Submit a pull request.

---

## License

This project is public. Feel free to use and adapt it to your needs.
