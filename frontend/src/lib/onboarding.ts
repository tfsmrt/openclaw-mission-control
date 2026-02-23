type OnboardingProfileLike = {
  name?: string | null;
  timezone?: string | null;
};

export function isOnboardingComplete(
  profile: OnboardingProfileLike | null | undefined,
): boolean {
  if (!profile) return false;
  return Boolean(profile.name?.trim()) && Boolean(profile.timezone?.trim());
}
