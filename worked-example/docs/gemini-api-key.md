# Set up the Gemini API key for Gemma 4

Battery Race calls Gemma 4 through the Gemini API. For this app, use a Gemini API key from
Google AI Studio and name the setting `GEMINI_API_KEY`.

## 1. Create the key yourself

1. Open [Google AI Studio's API Keys page](https://aistudio.google.com/apikey) and sign in
   with your Google account. Review any terms yourself.
2. Use an existing project you control, or create a project through AI Studio. New users may
   already have a default project and key. If an existing Cloud project is missing, import it
   from AI Studio's Projects page first.
3. Choose **Create API key** if you need a new key, select your project and follow the dialog.
   Copy the key privately. Do not paste it into a coding-agent chat.

Google's [API key guide](https://ai.google.dev/gemini-api/docs/api-key) explains project setup,
key creation and permission errors. Check your project's available quota; creating a key does
not establish that a particular model call will succeed.

## 2. Save it beside app.py

Copy the included `sample.env` to `.env` in the same folder as `app.py`:

```bash
cp sample.env .env
```

If `.env` already exists, edit it instead of overwriting it. Open `.env` yourself in a plain-text
editor and replace the placeholder with your key. `sample.env` is safe to commit because it
contains only a placeholder; keep your real key exclusively in the private `.env` file.
For the published worked example, that is `worked-example/.env`, not the repository root or
`worked-example/data/.env`. For a separate reconstruction folder, use that folder's root.

Put this single line in it, replacing the placeholder with your actual key:

```dotenv
GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
```

Do not include the placeholder, angle brackets, backticks or `export`. Save as plain text with
no `.txt` extension. The leading dot is part of the filename; some file browsers hide dotfiles.

```text
worked-example/
  app.py
  .env           <-- your private local file
  requirements.txt
  data/
```

The app uses `python-dotenv` to load `.env` beside `app.py`, then reads `GEMINI_API_KEY`.
You do not need to export the key in a terminal. If that terminal already has `GEMINI_API_KEY`
set, its existing value takes precedence over `.env`; restart from a shell without that setting
if you intend to use the file's value.

## 3. Run and check

After completing the data setup, run the app from its folder:

```bash
.venv/bin/streamlit run app.py
```

Select a postcode with an ABS postal area, such as 5159 in the included snapshot. A successful
live answer appears under **Explained by Gemma 4**. The headless tests use a fake client and do
not verify your real key. If the app reports no key, check the filename, location and variable
name yourself, then restart it. Do not ask an agent to read or print the file.

Keep `.env` out of Git and screenshots. To check the ignore rule without displaying the key,
run `git check-ignore .env` from the app folder. It should report `.env`. Never commit the file.
