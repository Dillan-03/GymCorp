"""Extensions used on top of flask"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Main extensions
db = SQLAlchemy(session_options={"expire_on_commit": False})
bcrypt = Bcrypt()
babel = Babel()
migrate = Migrate(db=db)
csrf = CSRFProtect()

# Flask rate limiter
limiter = Limiter(
    get_remote_address,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://",
)

# Login manager extension
login_manager = LoginManager()
login_manager.login_view = "customer_bp.login"  # type: ignore
login_manager.login_message = "Please login"
login_manager.login_message_category = "info"