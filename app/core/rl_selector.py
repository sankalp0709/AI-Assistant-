import math

class RLActionSelector:
    def __init__(self):
        # Simulated historical success rates
        self.success_rates = {
            'respond': 0.8,
            'summarize': 0.7,
            'intent': 0.6,
            'default': 0.5
        }

    def select_action(self, state, actions):
        scores = []
        for action in actions:
            score = 0.0

            # Heuristic 1: Action type - 'respond' gets higher score if state contains keywords
            if action == 'respond' and any(kw in str(state).lower() for kw in ['question', 'urgent']):
                score += 2.0

            # Heuristic 2: Action length - shorter actions preferred
            score -= len(str(action)) * 0.1

            # Heuristic 3: Simulated historical success rates
            score += self.success_rates.get(action, 0.5)

            scores.append(score)

        # Apply softmax to convert scores to probabilities (no numpy)
        exp_scores = [math.exp(s) for s in scores]
        total = sum(exp_scores) if exp_scores else 1.0
        probabilities = [e / total for e in exp_scores]

        # Selected action: highest probability
        selected_idx = max(range(len(probabilities)), key=lambda i: probabilities[i]) if probabilities else 0
        selected_action = actions[selected_idx]

        # Full probability distribution
        prob_dist = {action: float(probabilities[i]) for i, action in enumerate(actions)}

        # Ranked actions list: sorted by probability descending
        ranked_indices = sorted(range(len(probabilities)), key=lambda i: probabilities[i], reverse=True)
        ranked_actions = [actions[i] for i in ranked_indices]

        return selected_action, prob_dist, ranked_actions
