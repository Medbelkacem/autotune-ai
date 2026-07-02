import * as SecureStore from "expo-secure-store";
import Constants from "expo-constants";

const BASE = (Constants.expoConfig?.extra as { apiUrl?: string })?.apiUrl ?? "http://localhost:8000";
const TOKEN_KEY = "atk";

export async function saveToken(t: string) {
  await SecureStore.setItemAsync(TOKEN_KEY, t);
}
export async function loadToken() {
  return SecureStore.getItemAsync(TOKEN_KEY);
}
export async function clearToken() {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const t = await loadToken();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  return fetch(`${BASE}/v1${path}`, { ...init, headers });
}

export async function apiJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const r = await apiFetch(path, init);
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}
