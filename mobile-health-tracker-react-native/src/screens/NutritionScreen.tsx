import React from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { Card } from '@/components/Card';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { useAppSelector } from '@/hooks/redux';
import { logMeal } from '@/services/logging';
import { store } from '@/store';
import { createId } from '@/utils/id';
import { humanDate, nowIso } from '@/utils/time';

export function NutritionScreen() {
  const meals = useAppSelector((state) => state.nutrition.items);

  async function handleQuickAdd() {
    const now = nowIso();
    await logMeal(store, {
      id: createId('meal'),
      mealType: 'lunch',
      calories: 610,
      proteinGrams: 43,
      carbsGrams: 52,
      fatGrams: 21,
      date: now,
      updatedAt: now,
      syncStatus: 'pending',
    });
    Alert.alert('Meal logged', 'A demo meal was saved locally and queued for sync.');
  }

  return (
    <Screen title="Nutrition" subtitle="Track intake even when you are offline and sync later.">
      <PrimaryButton title="Quick add meal" onPress={handleQuickAdd} />
      {meals.map((meal) => (
        <Card key={meal.id}>
          <View style={styles.header}>
            <Text style={styles.title}>{meal.mealType}</Text>
            <Text style={styles.meta}>{meal.calories} kcal</Text>
          </View>
          <Text style={styles.meta}>{humanDate(meal.date)}</Text>
          <Text style={styles.meta}>Protein {meal.proteinGrams}g · Carbs {meal.carbsGrams}g · Fat {meal.fatGrams}g</Text>
          <Text style={styles.meta}>Sync state: {meal.syncStatus}</Text>
        </Card>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 17, fontWeight: '700', color: '#14213d', textTransform: 'capitalize' },
  meta: { fontSize: 13, color: '#52607a', lineHeight: 20 },
});
