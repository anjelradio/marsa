import { tokenStore } from "./token-store";

// El proveedor de autenticación definirá cómo obtener y renovar el token.
export async function getJWT(): Promise<string | null> {
  return tokenStore.get();
}

export async function refreshJWT(): Promise<string | null> {
  clearJWT();
  return null;
}

export function clearJWT(): void {
  tokenStore.clear();
}
