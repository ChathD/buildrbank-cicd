# BuildrBank · ship it without typing

Last week you put this agent on the internet by hand. Eleven commands —
build, tag, push, `ssh`, pull, run. It worked.

Do that five times a day and one day you will skip one.

This repo is the same project with one thing added: a file that writes those
eleven commands down, so a machine types them instead of you.

Nothing about the application changes. Same image, same server, same Docker
Hub, same commands. Only the typist changes.

```
push to a branch ──▶ test                                   stops here
push to main     ──▶ test ──▶ build & push ──▶ deploy ──▶ is it really up?
```

A branch gets you the tests and nothing else. That is what makes a branch a
safe place to be wrong.

---

## Before you start

| | |
|---|---|
| **Your `.env` from Week 5** | same keys, same Supabase project. Nothing to redo. |
| **GitHub** | Actions is free and unlimited on public repos |
| **Docker Hub** | the image you pushed last week is still sitting there |
| **AWS** | we build a fresh server today |

Lost your `.env`, or starting clean? Do
[Starting from scratch](#starting-from-scratch) first — five steps, about
twenty minutes — then come back here.

---

## 1 · Fork it

Actions only runs in a repo you own. **Fork**, top right of this page.

```bash
git clone https://github.com/YOUR-NAME/buildrbank-cicd.git
cd buildrbank-cicd
cp ../buildrbank-deploy/.env .env        # the one file that is never in git
```

Prove it still works before you change anything:

```bash
python3.12 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python scripts/check.py
```

**Checkpoint —** six green ticks.

---

## 2 · A server, and an address that stays

### Launch it

EC2 → **Launch instance**.

| | |
|---|---|
| Image | Ubuntu, 64-bit **x86** |
| Size | `t3.micro` |
| Key pair | download the `.pem` — you only get it once |
| Firewall | allow **22** and **8000**, source **Anywhere-IPv4** |

That firewall setting is wider than last week's. [Step 3](#3--why-port-22-is-open-to-everyone)
explains why it has to be, and what it costs.

### Give it an address that stays

The public IP that came with the instance is on loan. Stop the instance,
start it again, and AWS hands you a different one.

That was survivable when you typed the address yourself. It is not
survivable now, because you are about to write that address into a GitHub
secret. If it changes, the pipeline keeps deploying to an address that is
no longer yours, and the error will look nothing like "the IP changed".

An **Elastic IP** is an address AWS sets aside for you and does not take back.

EC2 → **Elastic IPs** (left menu, under *Network & Security*)

1. **Allocate Elastic IP address** → Allocate
2. select it → **Actions** → **Associate Elastic IP address**
3. Resource type **Instance** → choose your instance → **Associate**

From here on, that is *the* address. Use it in `ssh`, in your browser, and
in the `EC2_HOST` secret.

> **What it costs, and the trap.** AWS charges $0.005 per hour for every
> public IPv4 address — about $3.65 a month. The EC2 free tier covers 750
> hours a month of an address **attached to a running instance**, which is
> one address, all month, free.
>
> The trap is the other case. An Elastic IP you allocated and then left
> *unattached* is billed at the full rate, free tier or not. So when you
> terminate the instance at the end of the course, **release the Elastic IP
> as well** — EC2 → Elastic IPs → select → Actions → **Release**. Otherwise
> you go on paying for an address that points at nothing.

### Walk in and install Docker

```bash
chmod 400 builder-bank.pem
scp -i builder-bank.pem .env ubuntu@YOUR-ELASTIC-IP:~
ssh -i builder-bank.pem ubuntu@YOUR-ELASTIC-IP

curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu                 # then log out and back in
chmod 600 ~/.env
```

**Checkpoint —** `docker ps` runs without `sudo`.

### Start it once, by hand

Your image from last week is still on Docker Hub. You do not need to build
anything to get back on the air:

```bash
docker login
docker run -d --name bank --restart unless-stopped \
  -p 8000:8000 --env-file ~/.env YOUR-NAME/buildrbank:v1
```

**Checkpoint —** `http://YOUR-ELASTIC-IP:8000` answers.

That is the last time you type any of this.

---

## 3 · Why port 22 is open to everyone

Last week the rule said source **My IP** — yours, and nobody else's.

GitHub's build machines are not yours, and they do not have *an* address.
Actions runs on thousands of IPs that change constantly. There is no narrow
rule that lets them in, so the rule has to be **Anywhere-IPv4** (`0.0.0.0/0`).

Now say what that costs, out loud. Port 22 is reachable from every machine
on earth, and scanners find open ports within hours. The only thing between
them and your server is the key file you downloaded once. This image has
password login switched off, so that key is not one lock among several —
it is the lock. Two things follow:

- the `.pem` on your laptop is a serious credential now. Treat it like one.
- terminate the instance when the course ends, the way you would close an account.

The grown-up fix is to keep 22 shut and let the pipeline open it for its own
address, just long enough to deploy, then shut it again. That needs an AWS
user for the pipeline and two more secrets. It is the right answer for
anything real, and it is not what we are doing today.

---

## 4 · Three secrets and one variable

**Settings → Secrets and variables → Actions → New repository secret.**

| Name | Where it comes from |
|---|---|
| `DOCKERHUB_TOKEN` | Docker Hub → Account settings → Personal access tokens → Generate. **Not your password.** |
| `EC2_HOST` | your Elastic IP. Just the number — no `http://`, no `:8000` |
| `EC2_SSH_KEY` | the whole key file. `cat builder-bank.pem`, copy **everything**, including the `-----BEGIN` and `-----END` lines |

> `EC2_SSH_KEY` is where this goes wrong most often. Miss the BEGIN line or
> the final newline and the error you get back says `invalid format` and
> nothing else useful.

Now the **Variables** tab, right next to Secrets on the same page:

| Name | Value |
|---|---|
| `DOCKERHUB_USER` | your Docker Hub username |

Your username is not on the secrets list, and that is the lesson. It is
printed on every image you have ever pushed, and GitHub will show it back
to you any time you ask. A token you paste once and can never read again.
Two tabs, one page — GitHub built the distinction into the furniture.

> Until `DOCKERHUB_USER` is set, the build and deploy jobs **skip** rather
> than fail. That is why a freshly forked repo shows a green tick and two
> greyed-out boxes instead of a red cross.

The agent's own keys — OpenRouter, Supabase, Langfuse — are not on that list
either. They stay in `~/.env` on the server. The pipeline never calls a
model, so it never needs a model key.

---

## 5 · Fill in the five TODOs

Open [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml).
Five lines say `TODO`, each with a sentence of reading above it.

| | What goes there |
|---|---|
| 1 | the name of the secret holding your Docker Hub token |
| 2 | a second image tag — the commit's own id |
| 3 | the name of the secret holding your server's address |
| 4 | the name of the secret holding your key |
| 5 | the `docker run` line — the one you typed in step 2, word for word |

Commit and push. The first run will probably be red. Open it, read the log,
find the line. That is the skill.

---

## 6 · Change something, and watch it ship

```bash
git checkout -b my-first-change
```

Open `app/index.html` and change the header — `Support Console` to something
of your own. Then:

```bash
git add app/index.html
git commit -m "Rename the header"
git push -u origin my-first-change
```

Go to the **Actions** tab. Tests run; build and deploy sit greyed out,
because you are on a branch. And one test is **red**:

```
test_the_header_reads_support_console
```

That is not a bug. `tests/test_api.py` says the header reads "Support
Console", because somebody decided that once and wrote it down. You have
changed the decision — so change the test too, in the same commit.

Then open a pull request, watch it go green, and merge.

Merging puts it on `main`, which runs the whole pipeline: test, build, push,
deploy, and a last check that the server really answers. About four minutes.
Open `http://YOUR-ELASTIC-IP:8000` and your change is there — on a machine
you never logged into.

---

## When you need yesterday back

Every build pushes two tags: `:latest`, which moves, and `:<commit id>`,
which never does. So going back is not a rebuild. It is a different tag:

```bash
ssh -i builder-bank.pem ubuntu@YOUR-ELASTIC-IP
docker rm -f bank
docker run -d --name bank --restart unless-stopped \
  -p 8000:8000 --env-file ~/.env YOUR-NAME/buildrbank:THE-OLD-COMMIT-ID
```

That is the whole reason to tag twice.

---

## Running the tests on your laptop

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Ten tests, about a minute, **no keys needed** — `tests/conftest.py` supplies
fakes, and nothing in the suite calls a model or a database. That is exactly
why the test job is safe to run on a pull request from a stranger.

What the tests do **not** do is judge the agent's answers. You cannot
unit-test a reply: the same question can get two different answers and both
be right. We test the plumbing — the server starts, the page is served, the
procedures load, bad input is refused, `/health` leaks no keys — plus four
packaging facts that each exist because something really went wrong once.

Whether the answers are any good is what Langfuse is for, and that is a
different week.

---

## When it breaks

| What you see | Where to look |
|---|---|
| **`invalid format` in the deploy job** | `EC2_SSH_KEY`. Re-paste the whole `.pem`, BEGIN and END lines included. |
| **`insufficient scopes` when pushing the image** | The Docker Hub token is read-only. Note that *logging in* still succeeded — the scope only bites at the push, so the error arrives late and blames the wrong step. Generate a new token with **Read & Write**. |
| **`Permission denied (publickey)`** | right key, wrong user. It is `ubuntu`, not `ec2-user`. |
| **Deploy is green, the site is old** | you pushed `:latest` but ran a different tag on the server. Check TODO 6. |
| **`connection timed out` on ssh** | port 22 is still restricted to *My IP*. See [step 3](#3--why-port-22-is-open-to-everyone). |
| **Build and deploy say "skipped"** | the `DOCKERHUB_USER` variable is not set. Variables tab, not Secrets. |
| **It worked yesterday, now nothing deploys** | the instance restarted and the IP moved. That is what the Elastic IP prevents — check it is still *associated*. |
| **The container exits immediately** | `docker logs bank`. Almost always a missing key in `~/.env`. |
| **It answers, but knows nothing** | `seed-2-knowledge.sql` did not finish. Re-run it in the SQL editor. |

Read the log *before* you change anything. The first error is the real one.

---

## Starting from scratch

Only if you do not have a working `.env` from Week 5.

**1 · Supabase project.** New project → any name → nearest region → generate
the password and write it down. About two minutes to build.

**2 · Run the SQL.** Dashboard → **SQL Editor** → **New query** → paste →
**Run**. Three files, in this order:

| | | |
|---|---|---|
| [`scripts/schema.sql`](scripts/schema.sql) | 12 tables, 6 search functions | no data |
| [`scripts/seed-1-bank.sql`](scripts/seed-1-bank.sql) | customers, accounts, transactions | 5 KB |
| [`scripts/seed-2-knowledge.sql`](scripts/seed-2-knowledge.sql) | the handbook and the procedures | 450 KB — give it a moment |

All three are safe to run more than once.

> **Supabase will warn you: "Potential issues detected".** Choose
> **Run without RLS** — *not* the green button. The app signs in with the
> publishable key, and Row Level Security with no policies blocks every query
> it makes. It fails deceptively: the seed files still load, so the tables
> look correct, and only `check.py` tells you anything is wrong.

**3 · Keys.** `cp .env.example .env`, then fill it in. The Supabase values
are under **Project Overview** → the **Copy** button beside the project name.

**4 · Install.**

```bash
python3.12 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/check.py
```

> **`python: command not found`?** The venv is not active in that terminal.
> Run `activate` again — you need it in every new window. Use `python`, not
> `python3`: a Windows venv does not create a `python3`.

**5 · Run it.**

```bash
python -m uvicorn app.api:api --reload --port 8000
```

<http://localhost:8000> opens the chat page. Now go back to
[step 1](#1--fork-it).

---

## What is in here

```
app/
  settings.py     where the settings come from   <- the interesting file
  api.py          the web address
  index.html      the chat page
vendor/
  buildrbank/     the agent, copied verbatim. NEVER EDITED.
scripts/
  schema.sql      the 12 tables and 6 search functions
  seed-1-bank.sql, seed-2-knowledge.sql   the data
  check.py        tests each piece before you start the server
tests/            ten tests. No keys, no network, no opinions about answers.
.github/
  workflows/
    pipeline.yml  test -> build -> deploy. This week lives here.
docs/             diagrams, and how it all fits together
```

### Why the agent never notices

The agent keeps every setting in `vendor/buildrbank/config.py`, and normally
loads them itself. Its loader starts with "have I already been configured?" —
so `app/settings.py` fills that slot in first, and the agent finds the answer
waiting and skips its own loading entirely.

No subclassing, no patching, no fork. Delete `app/settings.py` and the agent
goes straight back to behaving exactly as it did in class.

---

## Honest limits

Carried over from Phase 1. Fine in a classroom, not fine on the open internet.

- **No login.** Whoever calls the API says who they are and is believed.
- **The procedures only narrate.** The agent will tell you your wire has been
  recalled. Nothing is written to the database.
- **One copy only.** Conversation memory is a file. Run a second server and
  the two will disagree about what you said.
- **The pipeline deploys to one machine.** It stops the old container before
  the new one is ready, so there are a few seconds of nothing. Real
  deployments start the new one first and only then let go of the old.

That last one is not a bug to fix today. It is what "zero downtime" means,
and it is a different week.
