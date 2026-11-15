export interface EarthLandmark {
  id: string;
  name: string;
  type: string;
  coord: string;
  desc: string;
  positionClass: string;
  analogSiteId: string;
  comparedWithTargetId: "mars-jezero" | "moon-shackleton-rim";
}

export const EARTH_LANDMARKS: EarthLandmark[] = [
  {
    id: "atacama",
    name: "Salar de Atacama",
    type: "Análogo de Hiperaridez Marciana (Chile)",
    coord: "23,86° S · 69,13° W",
    desc: "El desierto no polar más árido de la Tierra, con salmueras de evaporitas, costras salinas y radiación UV extrema análogas a los depósitos fluviales y lacustres de Jezero.",
    positionClass: "top-[58%] left-[32%]",
    analogSiteId: "earth-atacama-desert",
    comparedWithTargetId: "mars-jezero",
  },
  {
    id: "mcmurdo",
    name: "Valles Secos de McMurdo",
    type: "Análogo de Criosfera Polar (Antártida)",
    coord: "77,50° S · 162,00° E",
    desc: "Desierto frío libre de hielo con permafrost seco, suelos regolíticos poligonales y temperaturas bajo cero constantes, idóneo para validar bases permanentes en Shackleton.",
    positionClass: "top-[82%] left-[64%]",
    analogSiteId: "earth-mcmurdo-dry-valleys",
    comparedWithTargetId: "moon-shackleton-rim",
  },
  {
    id: "rio_tinto",
    name: "Cuenca Minera de Río Tinto",
    type: "Análogo de Bioquímica y Sulfatos (España)",
    coord: "37,69° N · 6,55° W",
    desc: "Aguas ácidas con precipitados de jarosita y óxidos de hierro idénticos a los minerales detectados por los rovers en depósitos sedimentarios marcianos.",
    positionClass: "top-[36%] left-[46%]",
    analogSiteId: "earth-rio-tinto",
    comparedWithTargetId: "mars-jezero",
  },
  {
    id: "haughton",
    name: "Cráter de Impacto Haughton",
    type: "Análogo Dual Luna/Marte (Isla Devon, Canadá)",
    coord: "75,38° N · 89,67° W",
    desc: "Estructura de impacto de 23 km en el Alto Ártico con brechas de impacto, permafrost y cañones hidrológicos usados por la NASA y el Mars Institute para probar rovers y trajes EVA.",
    positionClass: "top-[22%] left-[29%]",
    analogSiteId: "earth-haughton-impact-crater",
    comparedWithTargetId: "moon-shackleton-rim",
  },
  {
    id: "askja",
    name: "Caldera de Askja",
    type: "Análogo de Basalto Lunar (Islandia)",
    coord: "65,03° N · 16,75° W",
    desc: "Campos de lava y tefra basáltica donde los astronautas del programa Apollo entrenaron en geología de campo antes de explorar la superficie lunar.",
    positionClass: "top-[26%] left-[44%]",
    analogSiteId: "earth-askja-caldera",
    comparedWithTargetId: "moon-shackleton-rim",
  },
];
