<script lang="ts">
	import {
		createEventDispatcher,
		tick
	} from "svelte";
	import { BlockTitle } from "@gradio/atoms";
	import { Copy, Check, Send, Plus, Trash } from "@gradio/icons";
	import { fade } from "svelte/transition";
	import { BaseDropdown } from "@gradio/dropdown";
	import type { SelectData, CopyData } from "@gradio/utils";
	import { DialogueLine } from "./utils";

	export let speakers: string[] = [];
	export let emotions: string[] = [];
	export let value: DialogueLine[] = [];
	export let value_is_output = false;
	export let placeholder = "Type here...";
	export let label: string;
	export let info: string | undefined = undefined;
	export let disabled = false;
	export let show_label = true;
	export let container = true;
	export let max_lines: number | undefined = undefined;
	export let show_copy_button = false;
	export let root: string;
	export let show_submit_button: boolean = true;

	export let server: {
    	format: (body: DialogueLine[]) => Promise<string>;
  	};


	let dialogue_lines: DialogueLine[] = [];
	let dialogue_container_element: HTMLDivElement; // Reference to the container
	
	// Emotion autocomplete state
	let showEmotionMenu = false;
	let currentLineIndex = -1;
	let emotionMenuPosition = { x: 0, y: 0 };
	let filtered_emotions: string[] = [];
	let input_elements: HTMLInputElement[] = [];
	let old_value = JSON.stringify(value);

	// Initialize the component
	$: if (value.length === 0 && dialogue_lines.length === 0) {
		dialogue_lines = [{ speaker: speakers[0], text: "" }];
	}

	$: {
		// Ensure inputElements array has the same length as dialogueLines
		if (dialogue_lines.length > input_elements.length) {
			// Add null placeholders for new lines
			input_elements = [
				...input_elements,
				...Array(dialogue_lines.length - input_elements.length).fill(null)
			];
		} else if (dialogue_lines.length < input_elements.length) {
			// Trim extra elements
			input_elements = input_elements.slice(0, dialogue_lines.length);
		}
	}

	function add_line(index: number): void {
		const newSpeaker = speakers.length > 0 ? speakers[0] : "";
		dialogue_lines = [
			...dialogue_lines.slice(0, index + 1),
			{ speaker: newSpeaker, text: "" },
			...dialogue_lines.slice(index + 1)
		];
		
		// Focus the new input after render cycle
		tick().then(() => {
			if (input_elements[index + 1]) {
				input_elements[index + 1].focus();
			}
		});
	}

	function delete_line(index: number): void {
		dialogue_lines = [
			...dialogue_lines.slice(0, index),
			...dialogue_lines.slice(index + 1)
		];
	}

	function update_line(index: number, key: keyof DialogueLine, value: string): void {
		dialogue_lines[index][key] = value;
		dialogue_lines = [...dialogue_lines];
	}

	function handle_input(event: Event, index: number): void {
		const input = event.target as HTMLInputElement;
		if (input && !input_elements[index]) {
			input_elements[index] = input;
		}
		
		const cursor_position = input.selectionStart || 0;
		const text = input.value;
		let show_menu = false;
    	let position_reference_index = -1; // Index in text used for caret position calculation

		if (text[cursor_position - 1] === ':') {
			currentLineIndex = index;
			position_reference_index = cursor_position; 
			const search_text = get_emotion_search_text(text, cursor_position);
			filtered_emotions = emotions.filter(emotion => 
				search_text === '' || emotion.toLowerCase().includes(search_text.toLowerCase())
			);
			show_menu = filtered_emotions.length > 0;
		} else {
			// Check if we're still typing in an emotion context
			const lastColonIndex = text.lastIndexOf(':', cursor_position - 1);
			if (lastColonIndex >= 0 && !text.substring(lastColonIndex + 1, cursor_position).includes(' ')) {
				currentLineIndex = index;
				position_reference_index = lastColonIndex + 1; // Position menu relative to the start of the potential emotion
				const searchText = text.substring(lastColonIndex + 1, cursor_position);
				filtered_emotions = emotions.filter(emotion => 
					searchText === '' || emotion.toLowerCase().includes(searchText.toLowerCase())
				);
				show_menu = filtered_emotions.length > 0;
			}
		}

		if (show_menu && position_reference_index !== -1 && dialogue_container_element) {
			const container_rect = dialogue_container_element.getBoundingClientRect();
			const input_rect = input.getBoundingClientRect();
			// Calculate the horizontal pixel offset of the character at positionReferenceIndex
			const caret_pixel_offset = get_caret_position(input, position_reference_index);

			// Calculate caret's absolute screen position
			// X: Input's left edge + caret's offset within the input
			// Y: Input's bottom edge (to position menu below)
			const caretScreenX = input_rect.left + caret_pixel_offset;
			const caretScreenY = input_rect.bottom; 

			// Convert absolute screen position to position relative to the container's top-left corner
			emotionMenuPosition = {
				x: caretScreenX - container_rect.left,
				y: caretScreenY - container_rect.top
			};
			
			showEmotionMenu = true;
		} else {
			showEmotionMenu = false;
		}
	}

	// Get the typed text after the last colon for filtering emotions
	function get_emotion_search_text(text: string, cursorPosition: number): string {
		const lastColonIndex = text.lastIndexOf(':', cursorPosition - 1);
		if (lastColonIndex >= 0) {
			return text.substring(lastColonIndex + 1, cursorPosition);
		}
		return '';
	}

	function get_caret_position(input: HTMLInputElement, position: number): number {
		const text = input.value.substring(0, position);
		const tempElement = document.createElement('span');
		tempElement.style.font = window.getComputedStyle(input).font;
		tempElement.style.position = 'absolute';
		tempElement.style.visibility = 'hidden';
		tempElement.textContent = text;
		document.body.appendChild(tempElement);
		const width = tempElement.getBoundingClientRect().width;
		document.body.removeChild(tempElement);
		return width;
	}

	function insert_emotion(emotion: string): void {
		if (currentLineIndex >= 0 && currentLineIndex < dialogue_lines.length) {
			const text = dialogue_lines[currentLineIndex].text;
			const currentInput = input_elements[currentLineIndex];
			const cursorPosition = currentInput?.selectionStart || 0;
			
			// Find the last colon before cursor
			const lastColonIndex = text.lastIndexOf(':', cursorPosition - 1);
			
			if (lastColonIndex >= 0) {
				// Replace text from colon to cursor with the emotion
				const newText = text.substring(0, lastColonIndex) + 
					`${emotion} ` + 
					text.substring(cursorPosition);
				
				update_line(currentLineIndex, "text", newText);
				
				// Move cursor to after the inserted emotion
				tick().then(() => {
					const updatedInput = input_elements[currentLineIndex];
					if (updatedInput) {
						const newCursorPosition = lastColonIndex + emotion.length + 1;
						updatedInput.setSelectionRange(newCursorPosition, newCursorPosition);
						updatedInput.focus();
					}
				});
			}
			
			showEmotionMenu = false;
		}
	}

	function handle_click_outside(event: MouseEvent): void {
		if (showEmotionMenu) {
			const target = event.target as Node;
			const emotionMenu = document.getElementById('emotion-menu');
			if (emotionMenu && !emotionMenu.contains(target)) {
				showEmotionMenu = false;
			}
		}
	}

	let copied = false;
	let timer: any;

	const dispatch = createEventDispatcher<{
		change: DialogueLine[];
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

	function sync_value(dialogueLines: DialogueLine[]): void {
		value = [...dialogueLines];
		if (JSON.stringify(value) !== old_value) {
			handle_change();
			old_value = JSON.stringify(value);
		}
	}

	console.log("emotions", emotions)


	$: sync_value(dialogue_lines);

	// Update on value changes from outside
	$: if (JSON.stringify(value) !== old_value) {
		handle_change();
		old_value = JSON.stringify(value);
		dialogue_lines = [...value];
	}

	async function handle_copy(): Promise<void> {
		if ("clipboard" in navigator) {
			const text = await server.format(value)
			await navigator.clipboard.writeText(text);
			dispatch("copy", { value: text });
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
</script>

<svelte:window on:click={handle_click_outside} />

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

	<div class="dialogue-container" bind:this={dialogue_container_element}>
		{#each dialogue_lines as line, i}
			<div class="dialogue-line">
				<div class="speaker-column">
					<BaseDropdown
						bind:value={line.speaker}
						on:change={() => update_line(i, "speaker", line.speaker)}
						disabled={disabled}
						choices={speakers.map(s => [s, s])}
						show_label={false}
						container={true}
					/>
				</div>
				<div class="text-column">
					<div class="input-container">
						<input 
							type="text" 
							bind:value={line.text} 
							placeholder={placeholder}
							disabled={disabled}
							on:input={(event) => handle_input(event, i)}
						on:focus={(event) => handle_input(event, i)}
						on:keydown={(event) => {
							if (event.key === 'Escape' && showEmotionMenu) {
								showEmotionMenu = false;
								event.preventDefault();
							}
						}}
							bind:this={input_elements[i]}
						/>
					</div>
				</div>
				{#if !!!max_lines || (max_lines && i < max_lines - 1)}
				<div class:action-column={i == 0}>
					<button 
						class="add-button" 
						on:click={() => add_line(i)}
						aria-label="Add new line"
						disabled={disabled}
					>
						<Plus />
					</button>
				</div>
				{/if}
				{#if i > 0}
				<div class="action-column">
					<button 
						class="delete-button" 
						on:click={() => delete_line(i)}
						aria-label="Remove current line"
						disabled={disabled}
					>
						<Trash />
					</button>
				</div>
				{/if}
			</div>
		{/each}
		
		{#if showEmotionMenu}
			<div 
				id="emotion-menu"
				class="emotion-menu" 
				style="left: {emotionMenuPosition.x}px; top: {emotionMenuPosition.y}px;"
				transition:fade={{ duration: 100 }}
			>
				{#each filtered_emotions as emotion}
					<button 
						class="emotion-item" 
						on:click={() => insert_emotion(emotion)}
					>
						{emotion}
					</button>
				{/each}
			</div>
		{/if}
	</div>

	{#if show_submit_button}
		<div class="submit-container">
			<button
				class="submit-button"
				on:click={handle_submit}
				disabled={disabled}
			>
				<Send />
			</button>
		</div>
	{/if}
</label>

<style>
	label {
		display: block;
		width: 100%;
	}

	.input-container {
		display: flex;
		position: relative;
		align-items: flex-end;
	}

	.dialogue-container {
		border: none;
		border-radius: var(--input-radius);
		background: var(--input-background-fill);
		padding: var(--spacing-md);
		margin-bottom: var(--spacing-sm);
		position: relative;
	}

	.dialogue-line {
		display: flex;
		align-items: center;
		margin-bottom: var(--spacing-sm);
	}

	.speaker-column {
		flex: 0 0 150px;
		margin-right: var(--spacing-sm);
		display: flex;
		align-items: center;
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
		color: var(--body-text-color);
		background: var(--input-background-fill);
		min-height: 30px;
		flex-grow: 1;
		margin-top: 0px;
		margin-bottom: 0px;
		resize: none;
		z-index: 1;
		display: block;
		position: relative;
		background: var(--input-background-fill);
		padding: var(--input-padding);
		width: 100%;
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
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
		width: 25px;
		height: 25px;
		border: none;
		background: transparent;
		cursor: pointer;
	}

	.delete-button {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 15px;
		height: 15px;
	}

	.add-button:hover {
		color: var(--color-accent);
	}

	.emotion-menu {
		position: absolute;
		max-height: 200px;
		max-width: 300px;
		overflow-y: scroll;
		background: var(--background-fill-primary);
		border: 1px solid var(--border-color-primary);
		box-shadow: var(--shadow-drop-lg);
		border-radius: var(--container-radius);
		z-index: 100;
		display: flex;
		flex-direction: column;
	}

	.options {
		--window-padding: var(--size-8);
		position: fixed;
		z-index: var(--layer-top);
		margin-left: 0;
		box-shadow: var(--shadow-drop-lg);
		border-radius: var(--container-radius);
		background: var(--background-fill-primary);
		min-width: fit-content;
		max-width: inherit;
		overflow: auto;
		color: var(--body-text-color);
		list-style: none;
	}

	.item {
		display: flex;
		cursor: pointer;
		padding: var(--size-2);
		word-break: break-word;
	}

	.emotion-item {
		padding: var(--size-2);
		border: none;
		background: transparent;
		text-align: left;
		cursor: pointer;
		color: var(--body-text-color);
	}

	.emotion-item:hover {
		background-color: var(--color-background-secondary);
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
