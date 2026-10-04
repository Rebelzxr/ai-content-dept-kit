# 3-line task brief — 三行任务单

Give every AI task three lines before it starts. That is often enough to stop the two most common problems:
the AI stops too early, or it keeps going and does something you did not want.

每个 AI 任务开工前，先给它三行字。很多时候这就够了，能挡住两个最常见的问题：
AI 太早停下，或者一直做下去、做了你不想要的事。

## The template

```text
Done looks like: <the finished result, in one sentence, with a check you can see>
Check in when: <the situations where it must stop and ask you, and what to write down>
Stop if: <the things it must never do in this task>
```

## Example (a practice task we ran)

```text
Done looks like: summarise all 12 lines in complaints.txt into a table of actions with supporting complaint IDs; cover every ID and invent no owners or deadlines.
Check in when: the log leaves an owner, deadline, or policy unclear; label it unknown and list the question.
Stop if: resolving the task would require external access, sending a message, making a refund, or inventing facts.
```

## 中文版模板

```text
做完的样子：<一句话写出完成的结果，加一个看得到的检查>
什么时候先问我：<遇到哪些情况必须停下来问你，要先记下什么>
遇到这些就停：<这个任务里绝对不能做的事>
```

## 中文例子

```text
做完的样子：把 complaints.txt 里全部 12 行整理成一张「要做的事」表格，每一项附上对应的投诉编号；每个编号都要出现，不准编负责人或期限。
什么时候先问我：记录里看不出负责人、期限或规定时，标成「不知道」，并把问题列出来。
遇到这些就停：如果要上网、发信息、退款，或者要编造事实才能完成，就停下。
```

## How to write each line well

- **Done looks like** — make it checkable. "Cover every ID" can be checked. "Make it good" cannot.
- **Check in when** — name the unclear cases you expect. Tell it what to do there (label it, list the question), not just "ask me".
- **Stop if** — list actions with real-world effects: sending, paying, deleting, publishing, using outside accounts, making things up.

## 每一行怎么写

- **做完的样子**：要能检查。「每个编号都出现」可以检查；「写好一点」不能。
- **什么时候先问我**：先想到会卡住的情况，告诉它卡住时怎么做（标出来、列问题），不要只写「问我」。
- **遇到这些就停**：写会影响现实世界的动作：发出去、付钱、删除、发布、用外面的账号、编造内容。
