from app.agents.new_amex import Amex
from app.agents.new_mastercard import MasterCard
from app.agents.new_visa import Visa


PROVIDERS_MAP = {
    'amex': Amex,
    'mc': MasterCard,
    'visa': Visa
}