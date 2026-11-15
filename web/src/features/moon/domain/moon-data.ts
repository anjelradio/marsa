export interface MoonLandmark {
  id: string;
  name: string;
  type: string;
  coord: string;
  desc: string;
  positionClass: string;
  analogTargetId?: string;
  recommendedEarthSiteId?: string;
}

export const MOON_LANDMARKS: MoonLandmark[] = [
  {
    id: "shackleton",
    name: "Cráter Shackleton · Borde (LOLA Site04)",
    type: "Sitio Candidato Artemis III · NASA LOLA",
    coord: "89,9° S · 120,0° E",
    desc: "Cima del borde polar sur con picos de luz casi eterna e interior en sombra permanente (PSR) con depósitos de hielo de agua a 40 K.",
    positionClass: "top-[78%] left-[48%]",
    analogTargetId: "moon-shackleton-rim",
    recommendedEarthSiteId: "earth-mcmurdo-dry-valleys",
  },
  {
    id: "tranquillitatis",
    name: "Mare Tranquillitatis · Apollo 11",
    type: "Primer Alunizaje Humano (1969)",
    coord: "0,67° N · 23,47° E",
    desc: "Llanura basáltica rica en titanio e ilmenita donde Neil Armstrong y Buzz Aldrin recolectaron las primeras muestras lunares de suelo y roca.",
    positionClass: "top-[46%] left-[62%]",
    analogTargetId: "moon-shackleton-rim",
    recommendedEarthSiteId: "earth-askja-caldera",
  },
  {
    id: "tycho",
    name: "Cráter Tycho",
    type: "Cráter de Impacto Complejo Reciente",
    coord: "43,3° S · 11,4° W",
    desc: "Cráter de impacto de 85 km de diámetro y pico central de 1,6 km, famoso por su espectacular sistema de rayos eyectados visible desde la Tierra.",
    positionClass: "top-[68%] left-[36%]",
    analogTargetId: "moon-shackleton-rim",
    recommendedEarthSiteId: "earth-haughton-impact-crater",
  },
  {
    id: "aitken",
    name: "Cuenca Polo Sur-Aitken",
    type: "Mayor Cuenca de Impacto del Sistema Solar",
    coord: "53,0° S · 169,0° W",
    desc: "Depresión colosal de 2.500 km de diámetro y más de 8 km de profundidad que expone materiales del manto lunar profundo.",
    positionClass: "top-[32%] left-[28%]",
    analogTargetId: "moon-shackleton-rim",
    recommendedEarthSiteId: "earth-mcmurdo-dry-valleys",
  },
];
