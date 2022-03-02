# Working with GitHub

1. Clone the Lyve Cloud Repository: before you contribute to the Lyve Cloud, you'll have to Fork the Lyve Cloud repository to clone it into your private GitHub repository.
2. Click to expand: navigate to the repository homepage on GitHub.
3. Click Fork
4. Create [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token): PATs are an alternative to using passwords for authentication to GitHub when using the GitHub API or the command line.

### Syncing the fork with Repository

1. Config your git:
   ```
   $ git config --global user.name "Your Name" 
   $ git config --global user.email "Your Email" 
   ```

2. Clone your project by running the following command:
   ```
   $ git clone https://gitlab.com/<username>/Lyve-Cloud-solutions-samples.git
   ```

3. List the current configured remote repository for your fork:
   ```
   $ git remote -v
   ```
   **Sample Output:**
   ```
   origin  https://github.com/barviv-seagate/Lyve-Cloud-solutions-samples.git (fetch)
   origin  https://github.com/barviv-seagate/Lyve-Cloud-solutions-samples.git (push)
   ```

4. Specify a new remote upstream repository that will be synced with the fork:
   ```
   $ git remote add upstream https://github.com/lyvecloud-solutions/Lyve-Cloud-solutions-samples.git
   ```

5. Verify the new upstream repository you've specified for your fork:
   ```
   $ git remote -v
   ```
   **Sample Output:**
   ```
   origin   https://github.com/barviv-seagate/Lyve-Cloud-solutions-samples.git (fetch)
   origin   https://github.com/barviv-seagate/Lyve-Cloud-solutions-samples.git (push)
   upstream https://github.com/lyvecloud-solutions/Lyve-Cloud-solutions-samples.git (fetch)
   upstream https://github.com/lyvecloud-solutions/Lyve-Cloud-solutions-samples.git (push)
   ```

6. Make you origin repository same as an upstream repository:
   ```
   $ git fetch upstream
   ```

7. Create new branch by running the below mentioned command, if you are already not checked out:
   ```
   $ git checkout -b 'your-branch-name'
   ```
   **Sample Output:**
   ```
   C:> cd Lyve-Cloud-solutions-samples
   C:\Lyve-Cloud-solutions-samples>git checkout -b bari
   Switched to a new branch 'bari'
   ```

### Commit your Code

1. Check git status:
   ```
   $ git status
   ```
   **Sample Output:**
   ```
   C:\Lyve-Cloud-solutions-samples>git status
   On branch bari
   Untracked files:
     (use "git add <file>..." to include in what will be committed)
           working-with-git.md

   nothing added to commit but untracked files present (use "git add" to track)
   ```

2. Use the command below to add all the files that need to be pushed to the git staging area (dot indicates the addition of all the files. You can add some of the files, instead of the dot write the names of all the files with space between them):
   ```
   $ git add .
   ```
   **Sample Output:**
   ```
   C:\Lyve-Cloud-solutions-samples>git add working-with-git.md
   C:\Lyve-Cloud-solutions-samples>git status
   On branch bari
   Changes to be committed:
     (use "git restore --staged <file>..." to unstage)
           new file:   working-with-git.md
   ```

3. To commit your code changes use (m = message, s = signature):   
   **Note:** -s (DCO) = Developer Certificate of Origin and Contributor License Agreement, LyveCloud always requires DCO.
   ```
   $ git commit -s -m "your-comment"
   ```
   **Sample Output:**
   ```
   C:\Lyve-Cloud-solutions-samples>git commit -s -m "Add working with git"
   [bari 5236f34] Add working with git for developers
    1 file changed, 81 insertions(+)
    create mode 100644 working-with-git.md
   ```

4. Push the changes to your branch:
   ```
   $ git push origin 'your-branch-name'
   ```
   **Sample Output:**
   ```
   C:\Lyve-Cloud-solutions-samples>git push origin bari
   Enumerating objects: 4, done.
   Counting objects: 100% (4/4), done.
   Delta compression using up to 8 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 1.31 KiB | 1.31 MiB/s, done.
   Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
   remote: Resolving deltas: 100% (1/1), completed with 1 local object.
   remote:
   remote: Create a pull request for 'bari' on GitHub by visiting:
   remote:      https://github.com/lyvecloud-solutions/Lyve-Cloud-solutions-samples/pull/new/bari
   remote:
   To https://github.com/barviv-seagate/Lyve-Cloud-solutions-samples.git
    * [new branch]      bari -> bari
   Branch 'bari' set up to track remote branch 'bari' from 'origin'.
   ```

### Commit your Code

1. Use the command below to add all the files that need to be pushed to the git staging area:
   ```
   $ git add .
   ```

2. To commit your code changes use:
   ```
   $ git commit -s -m "comment"
   ```

3. Push the changes to your fork: 
   ```
   $ git push origin 'your-local-branch-name'
   ```
   **Sample Output:**
   ```
   ```

### Create a Pull Request

1. Once you Push changes to GitHub, the output will display a URL for creating a Pull Request, as shown in the sample code above.
2. Select the relevant repository branch from the Branches/Tags drop-down list.
3. Click Create pull request to create the pull request.
4. Add reviewers to your pull request to review and provide feedback on your changes.
