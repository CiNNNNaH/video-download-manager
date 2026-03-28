# Security Policy

## Scope
VDM is a desktop utility that shells out to external tools such as `yt-dlp`, `ffmpeg`, and `deno`.

## Reporting
If you find a security issue, do not post exploit details publicly first.
Report it privately with:
- affected version
- reproduction conditions
- impact summary
- whether external binaries or shell calls are involved

## Operational notes
- Review shell-based install/update behavior carefully.
- Do not trust arbitrary paths or filenames blindly.
- Prefer local portable binaries over uncontrolled PATH resolution when possible.
