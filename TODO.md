# TODO - Fix migrations/server errors (TruthGuard)

## Step 1: Collect exact error logs
- [ ] Ask user to paste the full traceback for:
  - `python manage.py makemigrations` (or any migration command they run)
  - `python manage.py runserver`

## Step 2: Fix guaranteed configuration issues found in code review
- [ ] Correct `INSTALLED_APPS` typo: change `'dasboard'` -> `'dashboard'`
- [ ] Ensure each app with models has migrations (or confirm none exist)

## Step 3: Re-run Django checks
- [x] Run `python manage.py check`
- [x] Run `python manage.py makemigrations`
- [x] Run `python manage.py migrate`

## Step 4: Re-run server
- [x] Run `python manage.py runserver` (startup OK; initial TemplateDoesNotExist fixed by adding TEMPLATES DIRS)


## Step 5: Address remaining model/migration issues (based on logs)
- [ ] Fix any `SystemCheckError`, model field errors, missing relations, app label mismatches, or migration conflicts

