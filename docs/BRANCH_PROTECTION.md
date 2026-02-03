# Branch Protection Setup Guide

This guide walks through setting up branch protection rules to enforce CI/CD checks before merging to the `master` branch.

## Prerequisites

- Repository admin access
- CI/CD pipeline is set up (see [CICD.md](CICD.md))
- At least one successful workflow run

## Step-by-Step Setup

### 1. Navigate to Branch Protection Settings

1. Go to your repository on GitHub
2. Click **Settings** (requires admin access)
3. In the left sidebar, click **Branches**
4. Under "Branch protection rules", click **Add rule** or **Add branch protection rule**

### 2. Configure Branch Name Pattern

- In the "Branch name pattern" field, enter: `master`
- If your default branch is `main`, enter: `main`
- You can also use patterns like `main*` to protect multiple branches

### 3. Enable Required Status Checks

Check the following boxes:

#### Required Status Checks to Pass
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging** (recommended)

#### Select Required Status Checks
In the search box that appears, select the following checks:
- `Test Python Pipeline (3.10)` - Tests on Python 3.10
- `Test Python Pipeline (3.11)` - Tests on Python 3.11  
- `Code Quality Checks` - Linting and syntax validation
- `Build Verification` - Import and build checks

**Note**: Status checks will only appear in the list after they've run at least once. If you don't see them:
1. Create a test PR first
2. Wait for the CI pipeline to run
3. Return to this settings page and select the checks

### 4. Additional Recommended Settings

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
  - Set "Required number of approvals before merging" to at least `1`
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
  - ✅ **Require review from Code Owners** (if you have a CODEOWNERS file)

#### Additional Restrictions
- ✅ **Require conversation resolution before merging** - Ensures all review comments are addressed
- ✅ **Require signed commits** (optional, for enhanced security)
- ✅ **Include administrators** - Applies rules to repository administrators too (recommended for consistency)

#### Allowed Actions
- ✅ **Allow force pushes** - Leave UNCHECKED (force pushes can break history)
- ✅ **Allow deletions** - Leave UNCHECKED (prevents accidental branch deletion)

### 5. Save Changes

Click **Create** or **Save changes** at the bottom of the page.

## Verification

After setting up branch protection:

### Test 1: Create a Test PR

1. Create a new branch:
   ```bash
   git checkout -b test-branch-protection
   echo "# Test" >> test.md
   git add test.md
   git commit -m "Test: Verify branch protection"
   git push origin test-branch-protection
   ```

2. Open a PR targeting `master`

3. Verify that:
   - CI checks start automatically
   - PR shows "Merging is blocked" until checks pass
   - "Merge" button is disabled while checks run

### Test 2: Verify Failing Checks Block Merge

1. Create a branch with a syntax error:
   ```bash
   git checkout -b test-failing-checks
   echo "def broken_function(" >> pipeline/test.py  # Syntax error
   git add pipeline/test.py
   git commit -m "Test: Introduce syntax error"
   git push origin test-failing-checks
   ```

2. Open a PR

3. Verify that:
   - CI checks fail
   - PR shows "All checks have failed"
   - "Merge" button remains disabled

4. Clean up:
   ```bash
   git checkout master
   git branch -D test-failing-checks
   git push origin --delete test-failing-checks
   ```

## What Happens Now?

With branch protection enabled:

### ✅ Pull Requests
- All PRs to `master` automatically trigger CI checks
- PRs cannot be merged until all required checks pass
- Status badges show check progress
- PR reviews are required (if configured)

### ✅ Direct Pushes
- Direct pushes to `master` are blocked (unless by admins with override)
- All changes must go through pull requests
- This ensures all code is reviewed and tested

### ✅ Failed Checks
- Contributors see which checks failed
- Click on "Details" to view logs
- Fix issues and push updates
- Checks re-run automatically

## Managing Exceptions

### Emergency Hotfixes

If you need to bypass protection for urgent fixes:

1. **Option 1**: Use emergency fix workflow (create this if needed)
2. **Option 2**: Admin override (discouraged)
   - Admins can use "Merge without waiting for requirements"
   - Should be used sparingly and documented
   - Follow up with a retro-active review

### Temporarily Disable Protection

Only for emergencies:
1. Go to Settings → Branches
2. Click "Edit" on the rule
3. Uncheck required checks
4. Make your changes
5. **Re-enable immediately**

## Updating Protection Rules

As the CI pipeline evolves:

### Adding New Checks

1. Add new job to `.github/workflows/ci.yml`
2. Let it run on a PR once
3. Go to Settings → Branches
4. Edit the rule
5. Select the new check

### Removing Checks

1. Uncheck the check in branch protection settings
2. Remove the job from the workflow file
3. Save changes

## Troubleshooting

### Status Checks Not Appearing

**Problem**: Can't find checks to select in branch protection settings

**Solutions**:
1. Ensure the workflow has run at least once
2. Check workflow name matches exactly (case-sensitive)
3. Verify workflow is triggered by `pull_request` events
4. Wait a few minutes and refresh the page

### Can't Merge Despite Green Checks

**Problem**: All checks pass but merge is still blocked

**Possible Causes**:
1. Branch is not up to date - click "Update branch"
2. Required reviews not completed
3. Conversation not resolved - check for unresolved comments
4. Administrator restrictions enabled

### Workflow Not Running

**Problem**: CI doesn't run on PR

**Solutions**:
1. Check workflow file is in `.github/workflows/`
2. Verify `on.pull_request.branches` includes your target branch
3. Check GitHub Actions are enabled for the repository
4. Review Actions tab for error messages

## Best Practices

### For Repository Maintainers

1. **Set up protection early** - Before accepting contributions
2. **Test thoroughly** - Verify protection works as expected
3. **Document clearly** - Ensure contributors understand requirements
4. **Review regularly** - Update rules as project evolves
5. **Monitor CI costs** - Track Action minutes usage

### For Contributors

1. **Test locally first** - Run `pytest` before pushing
2. **Keep PRs small** - Easier to review and test
3. **Monitor CI status** - Watch for failures
4. **Read failure logs** - Understand what failed and why
5. **Update dependencies** - Keep your branch current

## Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)
- [Repository CI/CD Guide](CICD.md)

## Questions?

For issues with branch protection:
1. Check this guide's troubleshooting section
2. Review GitHub's documentation
3. Open an issue with the `ci` label
4. Contact repository maintainers
