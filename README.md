## To start Project locally
- Run `create_ptable.py` to create two tables.
- Install the dependencies listed in `requirements.txt` via the command: `pip install -r requirements.txt`.
- Place two models `preTW2v_wv.model` and `preTW2v_wv.model.vectors.npy` in the same directory as `main.py`.
- Run the project using the command: `python main.py`.
- The project will be hosted at `http://127.0.0.1:5000`.

## Important notes
- The `BEARER_TOKEN` in `tweets_roberta.py` file may expire, so it needs to be regenerated and replaced.
- To regenerate the token, follow the steps provided at: `https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens`.
- The username and password provided are `username = 'username'` and `password='password'`.
- DataBase steps in `main.py` are commented out, uncomment them once the database is integrated.
