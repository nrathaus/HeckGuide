from django import forms
from .models import Webhooks


class TokenCalculatorForm(forms.Form):
    token1 = forms.IntegerField(label="500", initial=0)
    token2 = forms.IntegerField(label="1K", initial=0)
    token3 = forms.IntegerField(label="2.5K", initial=0)
    token4 = forms.IntegerField(label="5K", initial=0)
    token5 = forms.IntegerField(label="10K", initial=0)
    token6 = forms.IntegerField(label="25K", initial=0)
    token7 = forms.IntegerField(label="50K", initial=0)
    token8 = forms.IntegerField(label="100K", initial=0)
    token9 = forms.IntegerField(label="250K", initial=0)
    token10 = forms.IntegerField(label="500K", initial=0)
    token11 = forms.IntegerField(label="1M", initial=0)


class BrewCalculatorForm(forms.Form):
    token1 = forms.IntegerField(label="10", initial=0)
    token2 = forms.IntegerField(label="25", initial=0)
    token3 = forms.IntegerField(label="50", initial=0)
    token4 = forms.IntegerField(label="100", initial=0)
    token5 = forms.IntegerField(label="250", initial=0)


TROOPMIGHT_CHOICES = (
    ("1", "Train"),
    ("2", "Kill"),
)


class TroopMightForm(forms.Form):
    might = forms.IntegerField(label="Might", initial=0)
    trainkill = forms.ChoiceField(label="Train/Kill", choices=TROOPMIGHT_CHOICES)
    troops = forms.IntegerField(label="Troops", initial=0)


ALLYSTAT_CHOICES = (
    ("1", "Grasslands"),
    ("2", "Badlands"),
    ("3", "Swamplands"),
)


class AllyStatForm(forms.Form):
    price = forms.IntegerField(label="Price", initial=0)
    biome = forms.ChoiceField(label="Preferred Biome", choices=ALLYSTAT_CHOICES)


class RallyCalculatorForm(forms.Form):
    attackpower = forms.IntegerField(label="Attack Power", initial=0)
    bossstrength = forms.IntegerField(label="Boss Strength", initial=0)
    marchcap = forms.IntegerField(label="March Cap", initial=0)


class MasteryCalculatorForm(forms.Form):
    xpboost = forms.IntegerField(label="Dragon XP Boost", initial=0)
    gatherbonus = forms.IntegerField(label="Gather Rate Bonus", initial=0)
    attackbonus = forms.IntegerField(label="Hunt Attack Bonus", initial=0)
    marchcap = forms.IntegerField(label="March Capacity", initial=0)
    defcap = forms.IntegerField(label="City Defenders Cap", initial=0)
    attackboost = forms.IntegerField(label="Dragon Attack Boost", initial=0)
    defbonus = forms.IntegerField(label="Attacker/Defender Bonus", initial=0)
    statsforallies = forms.IntegerField(label="Bonus Stats for Allies", initial=0)
    bonusforallies = forms.IntegerField(label="Bonus from Allies", initial=0)
    marchboost = forms.IntegerField(label="Dragon March Speed Boost", initial=0)
    abilityboost = forms.IntegerField(label="Dragon Ability Boost", initial=0)
    marchcap2 = forms.IntegerField(label="March Capacity", initial=0)


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhooks
        fields = ("item", "hookurl", "realm")
