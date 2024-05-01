from pyasic.miners.device.makes import AuradineMake


class AuradineAT1500(AuradineMake):
    raw_model = "AT1500"
    expected_chips = 132
    expected_fans = 4
