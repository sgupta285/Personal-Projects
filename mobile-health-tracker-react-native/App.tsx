import React, { useEffect } from 'react';
import { Provider } from 'react-redux';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { store } from '@/store';
import { RootNavigator } from '@/navigation/RootNavigator';
import { bootstrapApp } from '@/services/bootstrap';

export default function App() {
  useEffect(() => {
    bootstrapApp(store).catch((error) => {
      console.warn('bootstrap failed', error);
    });
  }, []);

  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <NavigationContainer>
          <StatusBar style="dark" />
          <RootNavigator />
        </NavigationContainer>
      </SafeAreaProvider>
    </Provider>
  );
}
