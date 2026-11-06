# Единая конфигурация компиляции LaTeX (TeXiFy)

## Проблема

Раньше под каждый `.tex` создавалась отдельная конфигурация запуска TeXiFy с **абсолютными**
путями. Их накопилось 100+ (`.idea/workspace.xml`). Причина — стандартный путь вывода
`{mainFileParent}/frontend` не подходит под структуру проекта: `frontend` лежит не рядом с `.tex`,
а **на два уровня выше**, в корне работы (`termN/<работа>/frontend`), поэтому путь приходилось
править руками в каждой конфигурации.

## Решение — одна сущность (шаблон)

TeXiFy подставляет плейсхолдеры `{mainFileParent}` (папка главного файла) и `{projectDir}`
как обычную строку в абсолютный путь, а сегменты `..` затем разворачиваются на уровне ОС
(`File.mkdirs()` + `-output-directory`/`-aux-directory` у pdflatex). Документация прямо говорит, что
плейсхолдеры *«especially useful in template run configurations… when the main file is not yet known»*.

Значит, достаточно **одного шаблона** конфигурации. При запуске любого `.tex` (зелёная стрелка
в gutter / Shift+F10) TeXiFy создаёт **временную** конфигурацию, наследующую шаблон, с уже
правильными путями под конкретную работу. Временные конфигурации **сами вытесняются по FIFO**
(лимит ~5), поэтому не копятся. 100+ сохранённых конфигураций превращаются в **0** — единственный
источник истины это шаблон.

> ⚠️ Дисциплина: не нажимать «Save Configuration» на автосозданных временных конфигурациях —
> именно сохранение каждой и породило 100+ записей.

Проверено эмпирически (MiKTeX): компиляция `6.11.2_journal.tex` из `backend/tex` с
`-output-directory=../../frontend -aux-directory=../../acdn` кладёт PDF в `<работа>/frontend`,
а `.aux/.log/.toc` — прямо в `<работа>/acdn`. Лишней папки `../..` не создаётся.

## Настройки шаблона (единственная сущность)

| Поле | Значение | Зачем |
|---|---|---|
| Output directory | `{mainFileParent}/../../frontend` | `backend/tex` → `<работа>/frontend` (так у 99/99 работ) |
| Auxiliary files | `{projectDir}/acdn` | ЕДИНАЯ корневая папка служебных файлов на весь проект. ⚠️ в режиме «Use project SDK» TeXiFy это поле НЕ передаёт компилятору (флаг `-aux-directory` он добавляет только при явно выбранном MiKTeX SDK), поэтому aux ложится рядом с PDF в `frontend/`. Лечение — строка ниже |
| Custom compiler arguments | `-aux-directory=<абс. путь к корневой acdn>` (для этого проекта: `-aux-directory=C:/Users/user/PycharmProjects/random_tex_notes/acdn`; для resume: `-aux-directory=C:/Users/user/PycharmProjects/resume/acdn`) | флаг понимает сам движок MiKTeX (pdflatex/xelatex), поэтому работает при любом Distribution; в `frontend/` остаются только PDF. Поскольку acdn одна на весь проект, абсолютный путь одинаков для всех работ — никакой зависимости от `{mainFileParent}` |
| Working directory | `{mainFileParent}` | ⚠️ ОБЯЗАТЕЛЬНО: иначе относительные `\input{}` и `\graphicspath{{images/}}` не находятся |
| Always compile at least twice | ✔ | надёжные ссылки/оглавление/`\pageref{LastPage}` |
| Compiler / PDF viewer | pdfLaTeX / SumatraPDF (focus on) | как было |
| LaTeX Distribution | **Use project SDK** | ⚠️ НЕ «TeX Live»! В режиме TeX Live TeXiFy запускает pdflatex из неверного рабочего каталога → `! LaTeX Error: File '…' not found` на `\input`. «Use project SDK» запускает pdflatex из PATH (MiKTeX-portable) с рабочим каталогом `{mainFileParent}`. MiKTeX в списке нет — portable-установка не детектируется |

## Как применить

> ⚠️ **Только через интерфейс (способ A).** Прямая правка `workspace.xml` (способ B) НЕ работает надёжно:
> при следующем открытии PyCharm заново вставляет СВОЙ заводской шаблон LaTeX
> (`{projectDir}/out`, `compile-twice=false`, `MODULE_SDK`) рядом с вашим, и при запуске использует именно
> его — PDF уходит в `out/` в корне проекта, а не в `<работа>/frontend`. Шаблоном владеет PyCharm, поэтому
> задавать его надо через диалог шаблонов.

### A. Через интерфейс PyCharm (надёжно — РЕКОМЕНДУЕТСЯ)
1. **Run ▸ Edit Configurations…**
2. Слева удалить все 100+ конфигураций (выделить — минус).
3. **Edit configuration templates…** ▸ **LaTeX** — вписать поля из таблицы выше.
4. Там же **BibTeX** ▸ Auxiliary dir = `{projectDir}/acdn`, Distribution = MiKTeX.
5. OK. Дальше просто запускать любой `.tex` зелёной стрелкой — конфигурация создастся сама.

### B. Прямой правкой `.idea/workspace.xml` (НЕ РЕКОМЕНДУЕТСЯ — см. предупреждение выше)
`workspace.xml` пишется PyCharm при выходе, поэтому **PyCharm должен быть полностью закрыт**
(достаточно закрыть проект, но надёжнее выйти из IDE). Затем в компоненте
`<component name="RunManager">` заменить всё содержимое (шаблоны + все именованные конфигурации +
блок `<list>`) на два дефолтных шаблона:

```xml
  <component name="RunManager">
    <configuration default="true" type="LATEX_RUN_CONFIGURATION" factoryName="LaTeX configuration factory">
      <texify>
        <compiler>PDFLATEX</compiler>
        <compiler-path />
        <pdf-viewer>SumatraPDF</pdf-viewer>
        <require-focus>true</require-focus>
        <viewer-command />
        <compiler-arguments />
        <envs />
        <expand-macros-in-environment-variables>false</expand-macros-in-environment-variables>
        <before-run-command />
        <main-file />
        <output-path>{mainFileParent}/../../frontend</output-path>
        <auxil-path>{projectDir}/acdn</auxil-path>
        <working-directory>{mainFileParent}</working-directory>
        <compile-twice>true</compile-twice>
        <output-format>PDF</output-format>
        <latex-distribution>MODULE_SDK</latex-distribution>
        <has-been-run>false</has-been-run>
        <bib-run-config>[]</bib-run-config>
        <makeindex-run-config>[]</makeindex-run-config>
      </texify>
      <method v="2" />
    </configuration>
    <configuration default="true" type="BIBTEX_RUN_CONFIGURATION" factoryName="LaTeX configuration factory">
      <texify-bibtex>
        <compiler>BIBTEX</compiler>
        <compiler-path />
        <compiler-arguments />
        <envs />
        <main-file />
        <aux-dir />
        <latex-distribution>MODULE_SDK</latex-distribution>
      </texify-bibtex>
      <method v="2" />
    </configuration>
  </component>
```

(Из открывающего тега убрать `selected="LaTeX.6.10.4_report"` — выбранной именованной
конфигурации больше нет.)

## Папки (random_tex_notes)

```
termN/<работа>/             — термы в корне репо; внетермовые работы — в other/<работа>/
  backend/tex/*.tex        — исходники (рабочая папка компиляции)
  backend/tex/images/      — рисунки  (\graphicspath{{images/}})
  backend/*.xlsx|*.ipynb   — данные и обработка
  frontend/*.pdf           — результат (единственное, что коммитим из вывода)
acdn/                      — ЕДИНАЯ корневая папка служебных файлов LaTeX всего репо (в .gitignore)
config.md                  — этот файл
```

## Защита `\input`-фрагментов от случайной компиляции

Во фрагментах (не самостоятельных документах — theme*, подфайлы ml и т.п.) первые две строки:

```tex
%! root = <главный>.tex
\ifcsname ver@article.cls\endcsname\else\errmessage{This is an input fragment of <главный>.tex - compile <главный>.tex instead}\endinput\fi
```

- `%! root` — магический комментарий TeXiFy (ключ именно `root`, НЕ `TEX root`): даёт плагину
  правильный корень для навигации и разрешения путей. ⚠️ На запуск он НЕ влияет: TeXiFy при
  создании конфигурации из контекста всегда берёт сам файл (проверено по исходникам
  `LatexRunConfigurationProducer.kt`), т.е. «запустил фрагмент — собрался главный» в TeXiFy невозможно.
- Вторая строка — guard: при случайной автономной компиляции фрагмента (класс article ещё не
  загружен) pdflatex мгновенно (~1 с) останавливается с сообщением «This is an input fragment…»,
  без PDF и без многометрового лога. При `\input` из главного файла строка — no-op.
