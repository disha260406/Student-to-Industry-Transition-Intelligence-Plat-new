import requests
import re
import os
from collections import Counter

class GitHubAnalyzer:
    def __init__(self):
        token = os.environ.get('GITHUB_TOKEN', '')
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        if token:
            self.headers['Authorization'] = f'token {token}'

        self.skill_keywords = {
            'python': ['python', '.py', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', '.js', 'node', 'react', 'vue', 'angular', 'express'],
            'java': ['java', '.java', 'spring', 'maven', 'gradle'],
            'c++': ['cpp', 'c++', '.cpp', '.h', '.hpp'],
            'c#': ['csharp', 'c#', '.cs', 'dotnet', '.net'],
            'typescript': ['typescript', '.ts', 'tsx'],
            'go': ['golang', 'go', '.go'],
            'rust': ['rust', '.rs'],
            'php': ['php', '.php', 'laravel', 'symfony'],
            'ruby': ['ruby', '.rb', 'rails'],
            'swift': ['swift', '.swift', 'ios'],
            'kotlin': ['kotlin', '.kt', 'android'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'database'],
            'mongodb': ['mongodb', 'mongo', 'nosql'],
            'react': ['react', 'reactjs', 'jsx', 'tsx'],
            'angular': ['angular', 'angularjs'],
            'vue': ['vue', 'vuejs'],
            'docker': ['docker', 'dockerfile', 'container'],
            'kubernetes': ['kubernetes', 'k8s', 'kubectl'],
            'aws': ['aws', 'amazon', 'ec2', 's3', 'lambda'],
            'machine learning': ['ml', 'machine-learning', 'tensorflow', 'pytorch', 'scikit'],
            'data science': ['data-science', 'pandas', 'numpy', 'jupyter'],
            'html': ['html', '.html', 'html5'],
            'css': ['css', '.css', 'scss', 'sass'],
            'git': ['git', 'github', 'gitlab'],
        }

    def extract_username(self, github_url):
        """Extract GitHub username from URL or plain username"""
        github_url = github_url.strip()
        match = re.search(r'github\.com[/#:]?/?([^/\s?#]+)', github_url)
        if match:
            return match.group(1).replace('@', '')
        return github_url.replace('@', '').split('/')[0]

    def get_user_repos(self, username):
        try:
            url = f'https://api.github.com/users/{username}/repos'
            response = requests.get(url, headers=self.headers, timeout=10, params={'per_page': 30, 'sort': 'updated'})
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                return 'rate_limited'
            return []
        except Exception as e:
            print(f"Error fetching repos: {e}")
            return []

    def get_user_profile(self, username):
        try:
            url = f'https://api.github.com/users/{username}'
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                return 'rate_limited'
            return None
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None

    def get_repo_languages(self, username, repo_name):
        try:
            url = f'https://api.github.com/repos/{username}/{repo_name}/languages'
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}

    def get_recent_commits(self, username, repo_name):
        try:
            url = f'https://api.github.com/repos/{username}/{repo_name}/commits'
            response = requests.get(url, headers=self.headers, timeout=10, params={'per_page': 10})
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def check_profile_authenticity(self, profile, repos):
        from datetime import datetime
        authenticity_score = 100
        warnings = []

        if not profile or profile == 'rate_limited':
            return 50, []

        created_at = profile.get('created_at', '')
        if created_at:
            try:
                created_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                account_age_days = (datetime.now() - created_dt).days
                if account_age_days < 30:
                    authenticity_score -= 20
                    warnings.append(f'⚠️ Very new account (created {account_age_days} days ago)')
                elif account_age_days < 90:
                    authenticity_score -= 10
                    warnings.append(f'⚠️ New account (created {account_age_days} days ago)')
            except Exception:
                pass

        public_repos = profile.get('public_repos', 0)
        if public_repos == 0:
            authenticity_score -= 30
            warnings.append('⚠️ No public repositories')
        elif public_repos < 3:
            authenticity_score -= 15
            warnings.append(f'⚠️ Very few repositories ({public_repos})')

        followers = profile.get('followers', 0)
        if followers == 0:
            authenticity_score -= 5

        has_info = bool(profile.get('bio') or profile.get('name') or profile.get('company'))
        if not has_info:
            authenticity_score -= 10
            warnings.append('⚠️ Incomplete profile (no bio/name/company)')

        if repos and isinstance(repos, list):
            forked_count = sum(1 for r in repos if r.get('fork', False))
            if forked_count == len(repos) and len(repos) > 0:
                authenticity_score -= 25
                warnings.append('⚠️ All repositories are forked (no original work)')
            elif len(repos) > 0 and forked_count > len(repos) * 0.8:
                authenticity_score -= 15
                warnings.append(f'⚠️ Mostly forked repos ({forked_count}/{len(repos)})')

        return max(0, authenticity_score), warnings

    def analyze_repos(self, repos, username):
        detected_skills = Counter()
        repo_details = []
        all_languages = Counter()
        total_commits = 0

        for repo in repos[:10]:
            repo_name = repo.get('name', '').lower()
            repo_desc = (repo.get('description') or '').lower()
            repo_language = (repo.get('language') or '').lower()
            repo_topics = [t.lower() for t in repo.get('topics', [])]

            languages = self.get_repo_languages(username, repo.get('name'))
            for lang, bytes_count in languages.items():
                all_languages[lang.lower()] += bytes_count

            commits = self.get_recent_commits(username, repo.get('name'))
            commit_count = len(commits)
            total_commits += commit_count

            repo_text = f"{repo_name} {repo_desc} {repo_language} {' '.join(repo_topics)}"
            repo_skills = []

            for skill, keywords in self.skill_keywords.items():
                for keyword in keywords:
                    if keyword in repo_text or keyword in ' '.join(languages.keys()).lower():
                        detected_skills[skill] += 1
                        if skill not in repo_skills:
                            repo_skills.append(skill)
                        break

            if repo_skills or commit_count > 0:
                repo_details.append({
                    'name': repo.get('name'),
                    'description': repo.get('description'),
                    'language': repo.get('language'),
                    'languages': list(languages.keys())[:5],
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'is_fork': repo.get('fork', False),
                    'url': repo.get('html_url'),
                    'recent_commits': commit_count,
                    'detected_skills': repo_skills,
                    'updated_at': repo.get('updated_at')
                })

        total_bytes = sum(all_languages.values())
        language_percentages = {}
        if total_bytes > 0:
            for lang, bytes_count in all_languages.most_common(10):
                language_percentages[lang] = round((bytes_count / total_bytes) * 100, 1)

        return dict(detected_skills), repo_details, language_percentages, total_commits

    def verify_skills(self, github_url, claimed_skills):
        username = self.extract_username(github_url)
        if not username:
            return {'success': False, 'error': 'Invalid GitHub URL or username'}

        profile = self.get_user_profile(username)
        repos = self.get_user_repos(username)

        # Handle rate limit
        if repos == 'rate_limited' or profile == 'rate_limited':
            return {
                'success': False,
                'error': 'GitHub API rate limit exceeded. Add a GITHUB_TOKEN to .env to fix this. Try again in an hour or add your token.'
            }

        if not repos:
            return {
                'success': False,
                'error': f'No public repositories found for user: {username}',
                'profile_exists': profile is not None
            }

        authenticity_score, warnings = self.check_profile_authenticity(profile, repos)
        detected_skills, repo_details, language_percentages, total_commits = self.analyze_repos(repos, username)

        claimed_list = [s.strip().lower() for s in claimed_skills.split(',') if s.strip()]

        verified_skills = []
        unverified_skills = []
        for skill in claimed_list:
            if skill in detected_skills:
                verified_skills.append({'skill': skill, 'verified': True, 'project_count': detected_skills[skill]})
            else:
                unverified_skills.append({'skill': skill, 'verified': False, 'project_count': 0})

        additional_skills = [
            {'skill': skill, 'project_count': count}
            for skill, count in detected_skills.items()
            if skill not in claimed_list
        ]
        additional_skills.sort(key=lambda x: x['project_count'], reverse=True)

        total_claimed = len(claimed_list)
        total_verified = len(verified_skills)
        verification_score = (total_verified / total_claimed * 100) if total_claimed > 0 else 0

        return {
            'success': True,
            'username': username,
            'profile_url': f'https://github.com/{username}',
            'total_repos': len(repos),
            'total_commits_checked': total_commits,
            'languages_used': language_percentages,
            'authenticity_score': authenticity_score,
            'authenticity_warnings': warnings,
            'is_suspicious': authenticity_score < 50,
            'account_created': profile.get('created_at') if profile and profile != 'rate_limited' else None,
            'followers': profile.get('followers', 0) if profile and profile != 'rate_limited' else 0,
            'following': profile.get('following', 0) if profile and profile != 'rate_limited' else 0,
            'total_claimed_skills': total_claimed,
            'verified_skills': verified_skills,
            'unverified_skills': unverified_skills,
            'additional_skills': additional_skills[:10],
            'verification_score': round(verification_score, 2),
            'top_projects': repo_details[:5],
            'message': self._generate_message(verification_score, total_verified, total_claimed, authenticity_score)
        }

    def _generate_message(self, score, verified, total, authenticity_score):
        auth_warning = ""
        if authenticity_score < 50:
            auth_warning = " Your profile looks pretty new or inactive though."
        elif authenticity_score < 70:
            auth_warning = " Could use more activity on your profile."

        if score >= 80:
            return f"Found {verified}/{total} skills in your repos. Solid.{auth_warning}"
        elif score >= 60:
            return f"Verified {verified}/{total} skills. Build more projects to show the rest.{auth_warning}"
        elif score >= 40:
            return f"Only found {verified}/{total} skills in your code. Need more projects.{auth_warning}"
        else:
            return f"Just {verified}/{total} skills verified. Your GitHub doesn't match what you listed.{auth_warning}"
