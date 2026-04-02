import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { ChallengesScreen } from "../screens/ChallengesScreen";
import { FriendsScreen } from "../screens/FriendsScreen";
import { HomeScreen } from "../screens/HomeScreen";
import { ProfileScreen } from "../screens/ProfileScreen";

const Tab = createBottomTabNavigator();

export function RootNavigator() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Today" component={HomeScreen} />
      <Tab.Screen name="Challenges" component={ChallengesScreen} />
      <Tab.Screen name="Friends" component={FriendsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
