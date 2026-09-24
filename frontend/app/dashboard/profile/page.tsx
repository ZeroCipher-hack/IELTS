'use client';
import { useRouter } from 'next/navigation';
import { Camera, UserRound } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import { api, type User } from '@/components/product/api';
import { copy } from '@/components/product/i18n';

export default function ProfilePage() {
  const router = useRouter();
  const { t, say, user, displayName, language, busy, run, uploadAvatar, setUser, setLanguage, setNotice } = useProduct();
  if (!user) return null;

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>{t.profile}</h1>
          <p>{say('Shaxsiy ma’lumotlar va imtihon maqsadingiz.', 'Your personal details and exam goal.', 'Личные данные и цель экзамена.')}</p>
        </div>
      </div>
      <div className="profile-layout">
        <section className="panel profile-identity">
          <span className="profile-photo">{user.avatar ? <img src={user.avatar} alt={displayName || t.profile} /> : <UserRound size={48} />}</span>
          <h2>{displayName || t.name}</h2>
          <p className="profile-email">{user.email}</p>
          <label className={'secondary avatar-upload ' + (busy ? 'is-busy' : '')}>
            <Camera size={18} />{say('Rasm yuklash', 'Upload photo', 'Загрузить фото')}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              disabled={busy}
              onChange={(e) => {
                const file = e.target.files?.[0];
                e.target.value = '';
                if (file) void uploadAvatar(file);
              }}
            />
          </label>
          <small>JPG · PNG · WebP / 5 MB</small>
          {user.avatar && (
            <button
              className="text-button"
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  const result = await api<{ user: User }>('profile/', 'PATCH', { avatar: '' });
                  setUser(result.user);
                  setNotice(t.profileSaved);
                })
              }
            >
              {say('Rasmni olib tashlash', 'Remove photo', 'Удалить фото')}
            </button>
          )}
          <div className="profile-signin-note">
            <strong>{say('Email orqali kirish', 'Email sign-in', 'Вход по email')}</strong>
            <p>{say('Telefon hozir aloqa uchun saqlanadi. U orqali kirish hali yoqilmagan.', 'Your phone is saved for contact only. Phone sign-in is not enabled.', 'Телефон сохраняется для связи. Вход по номеру пока недоступен.')}</p>
          </div>
        </section>
        <form
          className="panel product-auth profile-form"
          onSubmit={(e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(e.currentTarget));
            void run(async () => {
              const result = await api<{ user: User }>('profile/', 'PATCH', data);
              setUser(result.user);
              setLanguage(result.user.language);
              setNotice(copy[result.user.language].profileSaved);
            });
          }}
        >
          <h2>{say('Siz haqingizda', 'About you', 'О вас')}</h2>
          <div className="profile-fields">
            <label>{t.name} *<input name="name" defaultValue={displayName} autoComplete="name" placeholder={say('Ismingizni kiriting', 'Enter your name', 'Введите имя')} required maxLength={80} /></label>
            <label>{say('Telefon (ixtiyoriy)', 'Phone (optional)', 'Телефон (необязательно)')}<input name="phone" type="tel" defaultValue={user.phone} autoComplete="tel" maxLength={24} placeholder="+998 90 123 45 67" /></label>
            <label>{say('Shahar', 'City', 'Город')}<input name="city" defaultValue={user.city} autoComplete="address-level2" maxLength={80} /></label>
            <label>
              {say('O‘qish turi', 'Study type', 'Тип обучения')}
              <select name="learner_type" defaultValue={user.learner_type}>
                <option value="">—</option>
                <option value="school">{say('Maktab', 'School', 'Школа')}</option>
                <option value="university">{say('Universitet', 'University', 'Университет')}</option>
                <option value="learning_center">{say('O‘quv markazi', 'Learning center', 'Учебный центр')}</option>
                <option value="independent">{say('Mustaqil', 'Independent', 'Самостоятельно')}</option>
              </select>
            </label>
            <label className="wide-field">{say('Maktab, universitet yoki o‘quv markazi', 'School, university or learning center', 'Школа, университет или учебный центр')}<input name="institution" defaultValue={user.institution} maxLength={160} /></label>
            <label>
              {t.target}
              <select name="target_band" defaultValue={user.target_band}>
                {Array.from({ length: 17 }, (_, i) => 1 + i * 0.5).map((n) => <option key={n} value={n}>{n.toFixed(1)}</option>)}
              </select>
            </label>
            <label>
              {t.language}
              <select name="language" defaultValue={language}>
                <option value="uz">O‘zbekcha</option>
                <option value="en">English</option>
                <option value="ru">Русский</option>
              </select>
            </label>
          </div>
          <button className="primary" disabled={busy}>{busy ? t.working : t.save}</button>
        </form>
      </div>
      <button className="secondary" onClick={() => router.push('/dashboard/speaking')}>{say('Speaking oynasini ochish', 'Open speaking studio', 'Открыть Speaking')}</button>
    </>
  );
}
