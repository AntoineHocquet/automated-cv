from pydantic import BaseModel, Field

class ChampsTraduits(BaseModel):
    ouverture: str = Field(
        default="Madame, Monsieur,",
        description="Ligne de salutation formelle pour une letter de motivation, e.g.: 'Madame, Monsieur', 'À l'attention du responsable du recrutement', etc."
    )
    corps: str = Field(
        default="",
        description="Corps principal de la lettre de motivation, e.g., 'Je suis interessé par votre offre de poste...'."
    )
    fermeture: str = Field(
        default="Bien cordialement",
        description="Fermeture polie de la lettre de motivation, e.g., 'Bien cordialement', 'Cordialement', 'Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées' etc."
    )


class UebersetzteAbschnitte(BaseModel):
    einleitung: str = Field(
        default="Sehr geehrte Damen und Herren,",
        description="Formelle Anrede am Anfang des Motivationsschreibens, z.B.: 'Sehr geehrte Damen und Herren', 'Sehr geehrter Herr...', etc."
    )
    hauptteil: str = Field(
        default="",
        description="Haupttext der Bewerbung, z.B.: 'Mit großem Interesse habe ich Ihre Stellenausschreibung gelesen...'."
    )
    schlussformel: str = Field(
        default="Mit freundlichen Gruessen",
        description="Höfliche Schlussformel am Ende der Bewerbung, z.B.: 'Mit freundlichen Gruessen', 'Mit besten Grüssen', etc."
    )