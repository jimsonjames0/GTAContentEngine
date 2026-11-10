from trend import Trend

class TrendRanker:
	def rank(self, trends, limit=10):
		ranked_trends = sorted(
			trends, 
			key = lambda trend: trend.score, 
			reverse=True
		)
		return ranked_trends[:limit]
