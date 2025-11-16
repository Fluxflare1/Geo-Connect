"use client";

import { useEffect, useState } from "react";
import { useRequireAuth } from "@/lib/use-require-auth";
import { fetchMe, updateProfile, changePassword, getCurrentUser } from "@/lib/auth";
import type { User } from "@/lib/types";
import { Button } from "@/components/ui/button";

export default function AccountPage() {
  const { user: initialUser, checking } = useRequireAuth();

  const [user, setUser] = useState<User | null>(initialUser);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSaved, setPasswordSaved] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    if (checking) return;

    async function loadProfile() {
      setLoadingProfile(true);
      setProfileError(null);
      try {
        // Prefer fresh /auth/me, fallback to local storage if needed
        const fresh = await fetchMe();
        setUser(fresh);
      } catch (err: any) {
        setProfileError(err.message || "Failed to load profile.");
        const local = getCurrentUser();
        if (local) {
          setUser(local);
        }
      } finally {
        setLoadingProfile(false);
      }
    }

    loadProfile();
  }, [checking]);

  async function handleProfileSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!user) return;

    setSavingProfile(true);
    setProfileSaved(false);
    setProfileError(null);

    try {
      const updated = await updateProfile({
        first_name: user.first_name,
        last_name: user.last_name,
        phone_number: user.phone_number
      });
      setUser(updated);
      setProfileSaved(true);
    } catch (err: any) {
      setProfileError(err.message || "Failed to update profile.");
    } finally {
      setSavingProfile(false);
    }
  }

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSaved(false);

    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError("All fields are required.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New password and confirmation do not match.");
      return;
    }

    setChangingPassword(true);
    try {
      await changePassword(oldPassword, newPassword);
      setPasswordSaved(true);
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      setPasswordError(err.message || "Failed to change password.");
    } finally {
      setChangingPassword(false);
    }
  }

  if (checking) {
    return (
      <div className="mt-6 text-sm text-gray-600">
        Checking your session…
      </div>
    );
  }

  return (
    <div className="mt-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-xl font-semibold">My account</h1>

      {/* Profile */}
      <div className="bg-white border rounded-lg shadow-sm p-4">
        <h2 className="text-sm font-semibold mb-3">Profile</h2>

        {loadingProfile && (
          <p className="text-xs text-gray-600 mb-2">
            Loading profile…
          </p>
        )}

        {profileError && (
          <div className="mb-3 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {profileError}
          </div>
        )}

        {profileSaved && (
          <div className="mb-3 rounded-md bg-green-50 px-3 py-2 text-xs text-green-700">
            Profile updated successfully.
          </div>
        )}

        {user && (
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium mb-1">
                Email (cannot be changed)
              </label>
              <input
                type="email"
                value={user.email}
                disabled
                className="block w-full rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium mb-1">
                  First name
                </label>
                <input
                  type="text"
                  value={user.first_name || ""}
                  onChange={e =>
                    setUser(prev =>
                      prev
                        ? { ...prev, first_name: e.target.value }
                        : prev
                    )
                  }
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">
                  Last name
                </label>
                <input
                  type="text"
                  value={user.last_name || ""}
                  onChange={e =>
                    setUser(prev =>
                      prev
                        ? { ...prev, last_name: e.target.value }
                        : prev
                    )
                  }
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium mb-1">
                Phone number
              </label>
              <input
                type="tel"
                value={user.phone_number || ""}
                onChange={e =>
                  setUser(prev =>
                    prev
                      ? { ...prev, phone_number: e.target.value }
                      : prev
                  )
                }
                className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                disabled={savingProfile}
              >
                {savingProfile ? "Saving…" : "Save changes"}
              </Button>
            </div>
          </form>
        )}
      </div>

      {/* Password */}
      <div className="bg-white border rounded-lg shadow-sm p-4">
        <h2 className="text-sm font-semibold mb-3">Change password</h2>

        {passwordError && (
          <div className="mb-3 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {passwordError}
          </div>
        )}

        {passwordSaved && (
          <div className="mb-3 rounded-md bg-green-50 px-3 py-2 text-xs text-green-700">
            Password updated successfully.
          </div>
        )}

        <form onSubmit={handlePasswordSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium mb-1">
              Current password
            </label>
            <input
              type="password"
              value={oldPassword}
              onChange={e => setOldPassword(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">
              New password
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1">
              Confirm new password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              disabled={changingPassword}
            >
              {changingPassword ? "Updating…" : "Update password"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
