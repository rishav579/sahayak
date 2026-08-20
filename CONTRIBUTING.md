# Contributing

Thanks for taking a look at Sahayak. Keep changes small enough to review, and prefer fixing the underlying behavior over adding another layer around it.

## Before opening a pull request

Run the checks that apply to your change:

```bash
# Frontend
cd frontend
npm ci
npm run build

# Backend syntax
cd ../backend
python -m compileall -q app
```

If a change touches authentication, ownership checks, uploads, media access, or AI output parsing, include a test or a short explanation of the validation that was performed. Do not commit `.env` files, credentials, uploaded media, build output, or dependency directories.

Please keep README changes factual. In particular, call out mock integrations and development-only behavior instead of presenting them as completed production features.
