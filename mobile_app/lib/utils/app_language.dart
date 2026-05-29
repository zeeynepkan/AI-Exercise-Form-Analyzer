
enum AppLanguage { tr, en }


extension AppLanguageX on AppLanguage {

  String get code => this == AppLanguage.tr ? 'tr' : 'en';

  String get label => this == AppLanguage.tr ? 'Türkçe' : 'English';

  String get ttsCode => this == AppLanguage.tr ? 'tr-TR' : 'en-US';
  
}
