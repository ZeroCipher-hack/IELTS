import type {Language} from './api';
const messages: Record<string, [string,string,string]> = {
  AI_RATE_LIMIT:['AI limiti tugagan. Administrator limitni tekshirgach qayta urinishi mumkin.','The AI quota was reached. An administrator can retry after checking the quota.','Лимит ИИ исчерпан. Администратор может повторить после проверки лимита.'],
  AI_INSUFFICIENT_AUDIO:['Aniq nutq baholash uchun yetarli emas. Uzunroq va tiniqroq javob yozib oling.','There is not enough clear speech to assess. Record a longer, clearer answer.','Недостаточно чёткой речи для оценки. Запишите более длинный и ясный ответ.'],
  AI_RECORDING_UNAVAILABLE:['Audio yozuv mavjud emas. Speaking mashqini qayta yozib topshiring.','The audio recording is unavailable. Record and submit a new Speaking practice.','Аудиозапись недоступна. Запишите и отправьте новую тренировку Speaking.'],
  AI_UNSUPPORTED_EVIDENCE:['AI dalili javob yoki matnga mos kelmadi. Ishonchsiz hisobot qabul qilinmadi.','The AI quotation did not match the source. The unsupported report was rejected.','Цитата ИИ не совпала с источником. Недостоверный отчёт отклонён.'],
  AI_INCOMPLETE_REPORT:['AI to‘liq hisobot yubormadi. Administrator qayta baholashni ishga tushirishi mumkin.','The AI report was incomplete. An administrator can retry the assessment.','Отчёт ИИ неполный. Администратор может повторить оценку.'],
  AI_RETRY_EXHAUSTED:['AI qayta urinishlari tugadi. Administratorga murojaat qiling.','AI retries have been exhausted. Contact an administrator.','Попытки оценки ИИ исчерпаны. Обратитесь к администратору.'],
};
export function assessmentMessage(code: string | undefined, language: Language): string | null {
  return code && messages[code] ? messages[code][language==='uz'?0:language==='en'?1:2] : null;
}
