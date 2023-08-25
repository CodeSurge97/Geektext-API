import os
from geektext import app

PORT = os.getenv("PORT")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
