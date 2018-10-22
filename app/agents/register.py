from app.agents.amex import Amex
from app.agents.mastercard import MasterCard
from app.agents.visa import Visa


PROVIDERS_MAP = {
    'amex': Amex,
    'mc': MasterCard,
    'visa': Visa
}
