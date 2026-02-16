# IBM Watsonx Configuration Guide

## Step 1: Get Your IBM Cloud API Key

1. Log in to [IBM Cloud](https://cloud.ibm.com/)
2. Click on **Manage** → **Access (IAM)** → **API keys**
3. Click **Create an IBM Cloud API key**
4. Give it a name (e.g., "Kisan-Assistant-Key") and description
5. Click **Create**
6. **IMPORTANT**: Copy and save your API key immediately (you won't be able to see it again!)

## Step 2: Get Your Watsonx Project ID

1. Go to [IBM Watsonx](https://dataplatform.cloud.ibm.com/wx/home)
2. Open your project (or create a new one if you don't have one)
3. Click on the **Manage** tab
4. Under **General** → **Details**, you'll find your **Project ID**
5. Copy the Project ID

Alternatively, you can find it in the URL:
- URL format: `https://dataplatform.cloud.ibm.com/projects/{PROJECT_ID}/...`
- The alphanumeric string after `/projects/` is your Project ID

## Step 3: Configure Your .env File

1. Copy the `.env.example` file to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in a text editor and update these values:
   ```
   IBM_WATSONX_API_KEY=your_actual_api_key_here
   IBM_WATSONX_PROJECT_ID=your_actual_project_id_here
   IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
   MODEL_NAME=ibm/granite-3-8b-instruct
   ```

3. Replace:
   - `your_actual_api_key_here` with your IBM Cloud API key from Step 1
   - `your_actual_project_id_here` with your Project ID from Step 2

4. **URL Options** (choose based on your region):
   - US South: `https://us-south.ml.cloud.ibm.com`
   - EU Frankfurt: `https://eu-de.ml.cloud.ibm.com`
   - EU London: `https://eu-gb.ml.cloud.ibm.com`
   - Tokyo: `https://jp-tok.ml.cloud.ibm.com`

## Step 4: Verify Your Setup

Run the test script:
```bash
python services/watsonx_service.py
```

If successful, you should see:
```
[SUCCESS] Watsonx service initialized successfully
[INFO] Test Query: How to control aphids in mustard?
[INFO] Generating response...
[SUCCESS] Response:
[Generated answer from Granite LLM]
```

## Step 5: Use Your Dataset

1. Place your actual KCC dataset file in the `data/` folder:
   ```
   data/raw_kcc.csv
   ```

2. Run the data preparation scripts:
   ```bash
   python services/data_preprocessing.py
   python services/generate_embeddings.py
   python services/faiss_store.py
   ```

3. Start the application:
   ```bash
   streamlit run app.py
   ```

## Troubleshooting

### Error: "Invalid API key"
- Double-check your API key in `.env`
- Make sure there are no extra spaces or quotes
- Verify the API key is still active in IBM Cloud

### Error: "Project not found"
- Verify your Project ID is correct
- Make sure you have access to the project in Watsonx
- Check that the project is in the same region as your URL

### Error: "Model not found"
- The Granite model might not be available in your region
- Try using: `ibm/granite-13b-chat-v2` or `meta-llama/llama-3-70b-instruct`
- Check available models in your Watsonx project

### Error: "Rate limit exceeded"
- You may have hit the free tier limit
- Wait a few minutes and try again
- Consider upgrading your IBM Cloud plan

## Available Granite Models

- `ibm/granite-3-8b-instruct` (recommended - latest)
- `ibm/granite-13b-chat-v2` (larger, more capable)
- `ibm/granite-13b-instruct-v2`
- `ibm/granite-20b-multilingual`

## Security Best Practices

1. **Never commit your `.env` file** to version control
2. **Keep your API key secret** - don't share it publicly
3. **Rotate your API keys** regularly
4. **Use separate API keys** for development and production
5. **Set up access policies** in IBM Cloud IAM

## Need Help?

- [IBM Watsonx Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html)
- [IBM Watsonx AI Python SDK](https://ibm.github.io/watsonx-ai-python-sdk/)
- [IBM Cloud Support](https://cloud.ibm.com/unifiedsupport/supportcenter)
