import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
from ragchallenge.api.api import app


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8082, log_level='info')
