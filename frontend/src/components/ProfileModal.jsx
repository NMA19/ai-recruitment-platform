/**
 * ProfileModal Component
 * Instagram-style profile editor with picture upload
 */

import { useState, useEffect, useRef } from 'react';
import { X, Upload, Camera, MapPin, Briefcase, Globe } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getAPIBaseURL } from '../services/api';

const AVATARS = [
  { id: 'orbit', emoji: '🌍', name: 'Orbit' },
  { id: 'nebula', emoji: '🌌', name: 'Nebula' },
  { id: 'galaxy', emoji: '🌠', name: 'Galaxy' },
  { id: 'cosmos', emoji: '🪐', name: 'Cosmos' },
];

export default function ProfileModal({ isOpen, onClose }) {
  const { user, profile, updateProfile, uploadProfilePicture } = useAuth();
  const fileInputRef = useRef(null);
  
  const [formData, setFormData] = useState({
    avatarId: 'orbit',
    bio: '',
    location: '',
    profession: '',
    website: '',
  });
  
  const [profilePicturePreview, setProfilePicturePreview] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingPicture, setIsUploadingPicture] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (profile) {
      setFormData({
        avatarId: profile.avatarId || 'orbit',
        bio: profile.bio || '',
        location: profile.location || '',
        profession: profile.profession || '',
        website: profile.website || '',
      });
      // Use profilePictureUrl if available, otherwise profilePicturePath
      if (profile.profilePictureUrl) {
        setProfilePicturePreview(profile.profilePictureUrl);
      } else if (profile.profile_picture_path) {
        setProfilePicturePreview(profile.profile_picture_path);
      } else {
        setProfilePicturePreview(null);
      }
    }
  }, [profile, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleAvatarSelect = (avatarId) => {
    setFormData(prev => ({
      ...prev,
      avatarId
    }));
  };

  const handlePictureChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Only PNG, JPG, GIF, or WebP images are allowed');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be less than 5MB');
      return;
    }

    setIsUploadingPicture(true);
    setError('');

    try {
      // Show preview immediately with data URL
      const reader = new FileReader();
      reader.onload = (event) => {
        setProfilePicturePreview(event.target?.result);
      };
      reader.readAsDataURL(file);

      // Upload to backend
      const response = await uploadProfilePicture(file);
      
      // Update preview with actual backend URL
      if (response.profilePictureUrl) {
        setProfilePicturePreview(response.profilePictureUrl);
      }
      
      setSuccess('Profile picture updated!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload picture');
      setProfilePicturePreview(profile?.profilePictureUrl || null);
    } finally {
      setIsUploadingPicture(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      await updateProfile({
        avatarId: formData.avatarId,
        bio: formData.bio,
        location: formData.location,
        profession: formData.profession,
        website: formData.website,
      });
      setSuccess('Profile updated successfully!');
      setTimeout(() => {
        setSuccess('');
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-100 dark:border-slate-800 sticky top-0 bg-white dark:bg-slate-900">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Profile</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Profile Picture Section */}
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              {/* Profile Picture */}
              <div className="w-32 h-32 rounded-full overflow-hidden bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center border-4 border-white dark:border-slate-800 shadow-lg">
                {profilePicturePreview ? (
                  <img
                    src={
                      profilePicturePreview.startsWith('http') || profilePicturePreview.startsWith('data:') 
                        ? profilePicturePreview 
                        : `${getAPIBaseURL()}${profilePicturePreview}`
                    }
                    alt="Profile"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      console.error('Failed to load image:', profilePicturePreview);
                      e.target.style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="text-5xl">
                    {AVATARS.find(a => a.id === formData.avatarId)?.emoji || '👤'}
                  </div>
                )}
              </div>

              {/* Upload Button */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handlePictureChange}
                accept="image/png,image/jpeg,image/gif,image/webp"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploadingPicture}
                className="absolute bottom-0 right-0 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-full p-3 shadow-lg transition transform hover:scale-110"
              >
                {isUploadingPicture ? (
                  <div className="animate-spin"><Camera size={16} /></div>
                ) : (
                  <Camera size={16} />
                )}
              </button>
            </div>

            {/* Email (read-only) */}
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
              <p className="text-lg font-medium text-gray-900 dark:text-white">{user.email}</p>
            </div>
          </div>

          {/* Messages */}
          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-xl text-sm font-medium">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 rounded-xl text-sm font-medium">
              ✓ {success}
            </div>
          )}

          {/* Avatar Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Avatar
            </label>
            <div className="grid grid-cols-4 gap-3">
              {AVATARS.map(avatar => (
                <button
                  key={avatar.id}
                  type="button"
                  onClick={() => handleAvatarSelect(avatar.id)}
                  className={`p-4 rounded-xl border-2 transition transform hover:scale-105 ${
                    formData.avatarId === avatar.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 shadow-md'
                      : 'border-gray-200 dark:border-slate-700 hover:border-gray-300'
                  }`}
                  title={avatar.name}
                >
                  <div className="text-3xl">{avatar.emoji}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Bio
            </label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              placeholder="Tell us about yourself..."
              maxLength={200}
              rows={3}
              className="w-full px-4 py-3 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition resize-none"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-right">
              {formData.bio.length}/200
            </p>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
              <MapPin size={16} className="text-blue-600" />
              Location
            </label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g., New York, USA"
              className="w-full px-4 py-3 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          {/* Profession */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
              <Briefcase size={16} className="text-blue-600" />
              Profession
            </label>
            <input
              type="text"
              name="profession"
              value={formData.profession}
              onChange={handleChange}
              placeholder="e.g., Software Engineer"
              className="w-full px-4 py-3 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          {/* Website */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
              <Globe size={16} className="text-blue-600" />
              Website
            </label>
            <input
              type="url"
              name="website"
              value={formData.website}
              onChange={handleChange}
              placeholder="https://example.com"
              className="w-full px-4 py-3 border border-gray-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 transition font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-blue-400 disabled:to-blue-400 text-white rounded-xl transition font-semibold flex items-center justify-center gap-2 shadow-lg"
            >
              <Upload size={18} />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
