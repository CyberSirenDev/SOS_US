import pandas as pd
from langdetect import detect, DetectorFactory
from textblob import TextBlob
import asyncio
import re

# Ensure consistent language detection
DetectorFactory.seed = 0

class MultilingualSentimentAnalyzer:
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'zh', 'ja', 'ko', 'ar']
        
        # Language patterns and configurations
        self.language_patterns = {
            'en': {'name': 'English', 'analyzer': self._analyze_english},
            'es': {'name': 'Spanish', 'analyzer': self._analyze_spanish},
            'fr': {'name': 'French', 'analyzer': self._analyze_french},
            'de': {'name': 'German', 'analyzer': self._analyze_german},
            'it': {'name': 'Italian', 'analyzer': self._analyze_italian},
            'pt': {'name': 'Portuguese', 'analyzer': self._analyze_portuguese},
            'nl': {'name': 'Dutch', 'analyzer': self._analyze_dutch},
            'ru': {'name': 'Russian', 'analyzer': self._analyze_russian},
            'zh': {'name': 'Chinese', 'analyzer': self._analyze_chinese},
            'ja': {'name': 'Japanese', 'analyzer': self._analyze_japanese},
            'ko': {'name': 'Korean', 'analyzer': self._analyze_korean},
            'ar': {'name': 'Arabic', 'analyzer': self._analyze_arabic}
        }
        
        print("✅ Multilingual Sentiment Analyzer initialized")

    def detect_language(self, text):
        """Detect language of the text"""
        try:
            if not text or len(text.strip()) < 10:
                return 'en'  # Default to English for short texts
            
            # Simple keyword-based detection as fallback
            lang_keywords = {
                'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
                'fr': ['le', 'la', 'de', 'et', 'à', 'en', 'un', 'est', 'pour', 'dans'],
                'de': ['der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'ist', 'sie'],
                'it': ['il', 'la', 'di', 'e', 'in', 'un', 'è', 'per', 'che', 'si'],
                'pt': ['o', 'a', 'de', 'e', 'em', 'um', 'é', 'para', 'com', 'não'],
                'nl': ['de', 'het', 'en', 'in', 'van', 'te', 'dat', 'is', 'een', 'op'],
                'ru': ['и', 'в', 'не', 'на', 'я', 'быть', 'с', 'что', 'а', 'по'],
                'zh': ['的', '一', '是', '在', '不', '了', '有', '和', '人', '这'],
                'ja': ['の', 'に', 'は', 'を', 'た', 'で', 'し', 'い', 'て', 'と'],
                'ko': ['이', '에', '는', '을', '의', '로', '다', '고', '하', '지'],
                'ar': ['ال', 'في', 'من', 'على', 'أن', 'ما', 'هو', 'إلى', 'كان', 'لا']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for lang, keywords in lang_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[lang] = score
            
            # If we have a clear winner from keywords, use it
            max_score = max(scores.values())
            if max_score > 2:
                best_lang = max(scores, key=scores.get)
                return best_lang
            
            # Fallback to langdetect
            return detect(text)
            
        except Exception as e:
            print(f"❌ Language detection failed: {e}")
            return 'en'  # Default to English

    def analyze_sentiment_multilingual(self, text, language_code='en'):
        """Analyze sentiment for text in various languages"""
        try:
            if language_code not in self.supported_languages:
                language_code = 'en'  # Default to English
            
            # Use the appropriate analyzer for the language
            analyzer_func = self.language_patterns.get(language_code, {}).get('analyzer', self._analyze_english)
            return analyzer_func(text)
            
        except Exception as e:
            print(f"❌ Multilingual sentiment analysis failed: {e}")
            return self._analyze_english(text)  # Fallback to English

    def _analyze_english(self, text):
        """Analyze English text sentiment"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive', polarity
        elif polarity < -0.1:
            return 'negative', polarity
        else:
            return 'neutral', polarity

    def _analyze_spanish(self, text):
        """Analyze Spanish text sentiment - basic implementation"""
        # Simple keyword-based analysis for Spanish
        positive_words = ['bueno', 'excelente', 'fantástico', 'maravilloso', 'genial', 'perfecto', 'amo', 'encanta']
        negative_words = ['malo', 'terrible', 'horrible', 'odio', 'problema', 'error', 'pésimo', 'decepcionado']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive', min(positive_count / 10, 1.0)
        elif negative_count > positive_count:
            return 'negative', min(negative_count / 10, -1.0)
        else:
            return 'neutral', 0.0

    def _analyze_french(self, text):
        """Analyze French text sentiment - basic implementation"""
        positive_words = ['bon', 'excellent', 'fantastique', 'merveilleux', 'génial', 'parfait', 'aime', 'adore']
        negative_words = ['mauvais', 'terrible', 'horrible', 'déteste', 'problème', 'erreur', 'épouvantable', 'déçu']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive', min(positive_count / 10, 1.0)
        elif negative_count > positive_count:
            return 'negative', min(negative_count / 10, -1.0)
        else:
            return 'neutral', 0.0

    # Similar basic implementations for other languages...
    def _analyze_german(self, text):
        return self._analyze_with_keywords(text, 
            ['gut', 'ausgezeichnet', 'fantastisch', 'wunderbar', 'großartig', 'perfekt', 'liebe', 'begeistert'],
            ['schlecht', 'schrecklich', 'furchtbar', 'hasse', 'problem', 'fehler', 'entsetzlich', 'enttäuscht']
        )

    def _analyze_italian(self, text):
        return self._analyze_with_keywords(text,
            ['buono', 'eccellente', 'fantastico', 'meraviglioso', 'ottimo', 'perfetto', 'amo', 'adoro'],
            ['cattivo', 'terribile', 'orribile', 'odio', 'problema', 'errore', 'pessimo', 'deluso']
        )

    def _analyze_portuguese(self, text):
        return self._analyze_with_keywords(text,
            ['bom', 'excelente', 'fantástico', 'maravilhoso', 'ótimo', 'perfeito', 'amo', 'adoro'],
            ['mau', 'terrível', 'horrível', 'odeio', 'problema', 'erro', 'péssimo', 'decepcionado']
        )

    def _analyze_dutch(self, text):
        return self._analyze_with_keywords(text,
            ['goed', 'uitstekend', 'fantastisch', 'prachtig', 'geweldig', 'perfect', 'hou', 'enthousiast'],
            ['slecht', 'verschrikkelijk', 'vreselijk', 'haat', 'probleem', 'fout', 'afschuwelijk', 'teleurgesteld']
        )

    def _analyze_russian(self, text):
        return self._analyze_with_keywords(text,
            ['хорошо', 'отлично', 'фантастика', 'замечательно', 'великолепно', 'идеально', 'люблю', 'восхищен'],
            ['плохо', 'ужасно', 'кошмар', 'ненавижу', 'проблема', 'ошибка', 'отвратительно', 'разочарован']
        )

    def _analyze_chinese(self, text):
        return self._analyze_with_keywords(text,
            ['好', '优秀', '精彩', '美妙', '伟大', '完美', '爱', '喜欢'],
            ['坏', '糟糕', '可怕', '恨', '问题', '错误', '恶劣', '失望']
        )

    def _analyze_japanese(self, text):
        return self._analyze_with_keywords(text,
            ['良い', '優秀', '素晴らしい', '見事', '偉大', '完璧', '愛', '好き'],
            ['悪い', 'ひどい', '恐ろしい', '嫌い', '問題', '誤り', '最悪', '失望']
        )

    def _analyze_korean(self, text):
        return self._analyze_with_keywords(text,
            ['좋은', '훌륭한', '환상적인', '멋진', '대단한', '완벽한', '사랑', '좋아하는'],
            ['나쁜', '끔찍한', '무서운', '싫어', '문제', '오류', '최악', '실망']
        )

    def _analyze_arabic(self, text):
        return self._analyze_with_keywords(text,
            ['جيد', 'ممتاز', 'رائع', 'جميل', 'عظيم', 'مثالي', 'أحب', 'معجب'],
            ['سيء', 'فظيع', 'مرعب', 'أكره', 'مشكلة', 'خطأ', 'مروع', 'خيبة أمل']
        )

    def _analyze_with_keywords(self, text, positive_words, negative_words):
        """Generic keyword-based sentiment analysis"""
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive', min(positive_count / 10, 1.0)
        elif negative_count > positive_count:
            return 'negative', min(negative_count / 10, -1.0)
        else:
            return 'neutral', 0.0

    def analyze_posts_multilingual(self, posts):
        """Analyze multiple posts with multilingual support"""
        if not posts:
            return {
                'total_posts': 0,
                'languages_detected': 0,
                'language_breakdown': {},
                'multilingual_support': True
            }, pd.DataFrame()
        
        results = []
        language_counts = {}
        
        for post in posts:
            if isinstance(post, dict) and 'text' in post:
                text = post['text']
                
                # Detect language
                language = self.detect_language(text)
                language_name = self.language_patterns.get(language, {}).get('name', 'Unknown')
                
                # Analyze sentiment
                sentiment, score = self.analyze_sentiment_multilingual(text, language)
                
                # Update language counts
                if language not in language_counts:
                    language_counts[language] = {
                        'count': 0,
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0,
                        'language_name': language_name
                    }
                
                language_counts[language]['count'] += 1
                language_counts[language][sentiment] += 1
                
                results.append({
                    'text': text,
                    'language': language,
                    'language_name': language_name,
                    'sentiment': sentiment,
                    'score': score,
                    'created_at': post.get('created_at', 'Unknown')
                })
        
        # Calculate percentages for each language
        for lang_data in language_counts.values():
            total = lang_data['count']
            lang_data['percentages'] = {
                'positive': (lang_data['positive'] / total) * 100 if total > 0 else 0,
                'neutral': (lang_data['neutral'] / total) * 100 if total > 0 else 0,
                'negative': (lang_data['negative'] / total) * 100 if total > 0 else 0
            }
        
        summary = {
            'total_posts': len(results),
            'languages_detected': len(language_counts),
            'language_breakdown': language_counts,
            'multilingual_support': True
        }
        
        df = pd.DataFrame(results)
        return summary, df

# Test the multilingual analyzer
def test_multilingual_analyzer():
    analyzer = MultilingualSentimentAnalyzer()
    
    test_posts = [
        {"text": "I love this product! It's absolutely amazing!"},
        {"text": "Este producto es terrible. No funciona para nada."},
        {"text": "Ce produit est excellent! Je l'adore!"},
        {"text": "Das Wetter ist heute schön. Nichts Besonderes."},
        {"text": "这个产品非常好用，我很喜欢！"},
        {"text": "Ceci est un test neutre sans émotion particulière."}
    ]
    
    print("Testing Multilingual Sentiment Analyzer:")
    summary, df = analyzer.analyze_posts_multilingual(test_posts)
    
    print(f"\nSummary:")
    print(f"Total posts: {summary['total_posts']}")
    print(f"Languages detected: {summary['languages_detected']}")
    
    print(f"\nLanguage breakdown:")
    for lang, data in summary['language_breakdown'].items():
        print(f"{data['language_name']}: {data['count']} posts")
        print(f"  Sentiment: {data['percentages']}")
    
    print(f"\nSample analysis:")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['text'][:30]}... -> {row['language_name']} ({row['sentiment']})")

if __name__ == "__main__":
    test_multilingual_analyzer()