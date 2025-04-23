<script lang="ts">
	import {
		beforeUpdate,
		afterUpdate,
		createEventDispatcher,
		tick
	} from "svelte";
	import { BlockTitle } from "@gradio/atoms";
	import { Copy, Check, Send, Plus } from "@gradio/icons";
	import { fade } from "svelte/transition";
	import type { SelectData, CopyData } from "@gradio/utils";

	export let speakers: string[] = [];
	export let emotions: string[] = [];
	export let value = "";
	export let value_is_output = false;
	export let lines = 1;
	export let placeholder = "Type here...";
	export let label: string;
	export let info: string | undefined = undefined;
	export let disabled = false;
	export let show_label = true;
	export let container = true;
	export let max_lines: number | undefined = undefined;
	export let show_copy_button = false;
	export let rtl = false;
	export let autofocus = false;
	export let text_align: "left" | "right" | undefined = undefined;
	export let autoscroll = true;
	export let max_length: number | undefined = undefined;
	export let root: string;

	// Dialogue state
	interface DialogueLine {
		speaker: string;
		text: string;
	}

	let dialogueLines: DialogueLine[] = [];
	
	// Initialize the component
	$: if (value === "" && dialogueLines.length === 0) {
		initializeDialogueLines();
	}

	// Initial setup and parsing
	async function initializeDialogueLines() {
		const defaultLine = { 
			speaker: speakers.length > 0 ? speakers[0] : "", 
			text: "" 
		};
		
		if (value === "") {
			dialogueLines = [defaultLine];
		} else {
			try {
				dialogueLines = parseDialogueValue(value);
			} catch (e) {
				dialogueLines = [{ 
					speaker: speakers.length > 0 ? speakers[0] : "", 
					text: value 
				}];
			}
		}
		
		// Initial sync from dialogueLines to value
		if (dialogueLines.length > 0) {
			value = formatDialogueValue(dialogueLines);
		}
	}

	// Sync changes when dialogueLines updates
	async function syncToValue() {
		value = formatDialogueValue(dialogueLines);
	}

	// Update on value changes from outside
	$: if (value) {
		(async () => {
			try {
				dialogueLines = parseDialogueValue(value);
			} catch (e) {
				if (speakers.length > 0 && dialogueLines.length === 0) {
					dialogueLines = [{ speaker: speakers[0], text: value }];
				} else if (dialogueLines.length === 0) {
					dialogueLines = [{ speaker: "", text: value }];
				}
			}
		})();
	}

	function parseDialogueValue(val: string): DialogueLine[] {
		try {
			return JSON.parse(val);
		} catch (e) {
			return val.split("\n").map(line => {
				const parts = line.split(":");
				if (parts.length >= 2) {
					const speaker = parts[0].trim();
					const text = parts.slice(1).join(":").trim();
					return { speaker, text };
				}
				return { speaker: speakers[0] || "", text: line.trim() };
			});
		}
	}

	function formatDialogueValue(lines: DialogueLine[]): string {
		return JSON.stringify(lines);
	}

	function addLine(index: number): void {
		const newSpeaker = speakers.length > 0 ? speakers[0] : "";
		dialogueLines = [
			...dialogueLines.slice(0, index + 1),
			{ speaker: newSpeaker, text: "" },
			...dialogueLines.slice(index + 1)
		];
		syncToValue();
	}

	function updateLine(index: number, key: keyof DialogueLine, value: string): void {
		dialogueLines[index][key] = value;
		dialogueLines = [...dialogueLines]; // Trigger reactivity
		syncToValue();
	}

	let copied = false;
	let timer: any;

	const dispatch = createEventDispatcher<{
		change: string;
		submit: undefined;
		blur: undefined;
		select: SelectData;
		input: undefined;
		focus: undefined;
		copy: CopyData;
	}>();

	function handle_change(): void {
		dispatch("change", value);
		if (!value_is_output) {
			dispatch("input");
		}
	}

	$: value, handle_change();

	async function handle_copy(): Promise<void> {
		if ("clipboard" in navigator) {
			await navigator.clipboard.writeText(value);
			dispatch("copy", { value: value });
			copy_feedback();
		}
	}

	function copy_feedback(): void {
		copied = true;
		if (timer) clearTimeout(timer);
		timer = setTimeout(() => {
			copied = false;
		}, 1000);
	}

	function handle_submit(): void {
		dispatch("submit");
	}

	$: console.log(dialogueLines);
</script>

<label class:container>
	{#if show_label && show_copy_button}
		{#if copied}
			<button
				in:fade={{ duration: 300 }}
				class="copy-button"
				aria-label="Copied"
				aria-roledescription="Text copied"><Check /></button
			>
		{:else}
			<button
				on:click={handle_copy}
				class="copy-button"
				aria-label="Copy"
				aria-roledescription="Copy text"><Copy /></button
			>
		{/if}
	{/if}
	
	<!-- svelte-ignore missing-declaration -->
	<BlockTitle {root} {show_label} {info}>{label}</BlockTitle>

	<div class="dialogue-container">
		{#each dialogueLines as line, i}
			<div class="dialogue-line">
				<div class="speaker-column">
					<select 
						bind:value={line.speaker} 
						on:change={() => updateLine(i, "speaker", line.speaker)}
						disabled={disabled}
					>
						{#if speakers.length === 0}
							<option value="">Select speaker</option>
						{/if}
						{#each speakers as speaker}
							<option value={speaker}>{speaker}</option>
						{/each}
					</select>
				</div>
				<div class="text-column">
					<input 
						type="text" 
						bind:value={line.text} 
						placeholder={placeholder}
						disabled={disabled}
					/>
				</div>
				<div class="action-column">
					<button 
						class="add-button" 
						on:click={() => addLine(i)}
						aria-label="Add new line"
						disabled={disabled}
					>
						<Plus />
					</button>
				</div>
			</div>
		{/each}
	</div>

	<div class="submit-container">
		<button
			class="submit-button"
			on:click={handle_submit}
			disabled={disabled}
		>
			<Send />
		</button>
	</div>
</label>

<style>
	label {
		display: block;
		width: 100%;
	}

	.dialogue-container {
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
		background: var(--input-background-fill);
		padding: var(--spacing-md);
		margin-bottom: var(--spacing-sm);
	}

	.dialogue-line {
		display: flex;
		align-items: center;
		margin-bottom: var(--spacing-sm);
	}

	.speaker-column {
		flex: 0 0 150px;
		margin-right: var(--spacing-sm);
	}

	.speaker-column select {
		width: 100%;
		padding: var(--spacing-sm);
		background-color: #f7d358;
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-sm);
		font-weight: bold;
	}

	.text-column {
		flex: 1;
		margin-right: var(--spacing-sm);
	}

	.text-column input {
		width: 100%;
		padding: var(--spacing-sm);
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-sm);
		background: rgb(100, 11, 11);
	}

	.action-column {
		flex: 0 0 40px;
		display: flex;
		justify-content: center;
	}

	.add-button {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 30px;
		height: 30px;
		border: none;
		background: transparent;
		cursor: pointer;
	}

	.add-button:hover {
		color: var(--color-accent);
	}

	.submit-container {
		display: flex;
		justify-content: flex-end;
	}

	.submit-button {
		border: none;
		text-align: center;
		text-decoration: none;
		font-size: 14px;
		cursor: pointer;
		border-radius: 15px;
		min-width: 30px;
		height: 30px;
		flex-shrink: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		background: var(--button-secondary-background-fill);
		color: var(--button-secondary-text-color);
	}

	.submit-button:hover {
		background: var(--button-secondary-background-fill-hover);
	}

	.submit-button:active {
		box-shadow: var(--button-shadow-active);
	}

	.submit-button :global(svg) {
		height: 22px;
		width: 22px;
	}

	.copy-button {
		display: flex;
		position: absolute;
		top: var(--block-label-margin);
		right: var(--block-label-margin);
		align-items: center;
		box-shadow: var(--shadow-drop);
		border: 1px solid var(--border-color-primary);
		border-top: none;
		border-right: none;
		border-radius: var(--block-label-right-radius);
		background: var(--block-label-background-fill);
		padding: 5px;
		width: 22px;
		height: 22px;
		overflow: hidden;
		color: var(--block-label-color);
		font: var(--font-sans);
		font-size: var(--button-small-text-size);
	}
</style>
