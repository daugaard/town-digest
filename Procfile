web: flask --app src/town_digest/app/main.py run
prefect_web: prefect server start
prefect_agent: sleep 2 && prefect worker start --pool default
