import { ActivitySnapshot } from '@/types/models';
import { nowIso } from '@/utils/time';

export interface HealthProvider {
  providerName: 'demo' | 'healthkit' | 'google_fit';
  readTodaySnapshot(): Promise<ActivitySnapshot>;
}

class DemoHealthProvider implements HealthProvider {
  providerName: 'demo' = 'demo';

  async readTodaySnapshot(): Promise<ActivitySnapshot> {
    return {
      steps: 8724,
      activeMinutes: 64,
      restingHeartRate: 58,
      source: 'demo',
      capturedAt: nowIso(),
    };
  }
}

class HealthKitProvider implements HealthProvider {
  providerName: 'healthkit' = 'healthkit';

  async readTodaySnapshot(): Promise<ActivitySnapshot> {
    return {
      steps: 0,
      activeMinutes: 0,
      source: 'healthkit',
      capturedAt: nowIso(),
    };
  }
}

class GoogleFitProvider implements HealthProvider {
  providerName: 'google_fit' = 'google_fit';

  async readTodaySnapshot(): Promise<ActivitySnapshot> {
    return {
      steps: 0,
      activeMinutes: 0,
      source: 'google_fit',
      capturedAt: nowIso(),
    };
  }
}

export function resolveHealthProvider(): HealthProvider {
  const mode = process.env.EXPO_PUBLIC_HEALTH_PROVIDER;
  if (mode === 'healthkit') {
    return new HealthKitProvider();
  }
  if (mode === 'google_fit') {
    return new GoogleFitProvider();
  }
  return new DemoHealthProvider();
}
