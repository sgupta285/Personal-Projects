import AsyncStorage from "@react-native-async-storage/async-storage";

const memory = new Map<string, string>();

export async function getItem(key: string) {
  try {
    return await AsyncStorage.getItem(key);
  } catch {
    return memory.get(key) ?? null;
  }
}

export async function setItem(key: string, value: string) {
  try {
    await AsyncStorage.setItem(key, value);
  } catch {
    memory.set(key, value);
  }
}
