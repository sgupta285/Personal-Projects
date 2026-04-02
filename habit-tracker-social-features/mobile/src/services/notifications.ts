import * as Notifications from "expo-notifications";

export async function registerForNotifications(): Promise<string | null> {
  try {
    const permission = await Notifications.requestPermissionsAsync();
    if (permission.status !== "granted") {
      return null;
    }
    const token = await Notifications.getExpoPushTokenAsync();
    return token.data;
  } catch {
    return "demo-device-token";
  }
}
