<script lang="ts">
	import { onMount } from 'svelte';
	import {
		beforeUpdate,
		afterUpdate,
		createEventDispatcher,
		tick
	} from "svelte";
	import { BlockTitle } from "@gradio/atoms";
	import { Copy, Check, Send, Square } from "@gradio/icons";
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

	let el: HTMLTextAreaElement | HTMLInputElement;
	let copied = false;
	let timer: any;
	let can_scroll: boolean;
	let previous_scroll_top = 0;
	let user_has_scrolled_up = false;
	let _max_lines: number;

	const show_textbox_border = false;

	$: if (max_lines === undefined) {
		_max_lines = Math.max(lines, 20);
	} else {
		_max_lines = Math.max(max_lines, lines);
	}

	$: value, el && lines !== _max_lines && resize({ target: el });

	$: if (value === null) value = "";

	const dispatch = createEventDispatcher<{
		change: string;
		submit: undefined;
		blur: undefined;
		select: SelectData;
		input: undefined;
		focus: undefined;
		copy: CopyData;
	}>();

	beforeUpdate(() => {
		can_scroll = el && el.offsetHeight + el.scrollTop > el.scrollHeight - 100;
	});

	const scroll = (): void => {
		if (can_scroll && autoscroll && !user_has_scrolled_up) {
			el.scrollTo(0, el.scrollHeight);
		}
	};

	function handle_change(): void {
		dispatch("change", value);
		if (!value_is_output) {
			dispatch("input");
		}
	}
	afterUpdate(() => {
		if (autofocus) {
			el.focus();
		}
		if (can_scroll && autoscroll) {
			scroll();
		}
		value_is_output = false;
	});
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

	function handle_select(event: Event): void {
		const target: HTMLTextAreaElement | HTMLInputElement = event.target as
			| HTMLTextAreaElement
			| HTMLInputElement;
		const text = target.value;
		const index: [number, number] = [
			target.selectionStart as number,
			target.selectionEnd as number
		];
		dispatch("select", { value: text.substring(...index), index: index });
	}

	async function handle_keypress(e: KeyboardEvent): Promise<void> {
		await tick();
		if (e.key === "Enter" && e.shiftKey && lines > 1) {
			e.preventDefault();
			dispatch("submit");
		} else if (
			e.key === "Enter" &&
			!e.shiftKey &&
			lines === 1 &&
			_max_lines >= 1
		) {
			e.preventDefault();
			dispatch("submit");
		}
	}

	function handle_scroll(event: Event): void {
		const target = event.target as HTMLElement;
		const current_scroll_top = target.scrollTop;
		if (current_scroll_top < previous_scroll_top) {
			user_has_scrolled_up = true;
		}
		previous_scroll_top = current_scroll_top;

		const max_scroll_top = target.scrollHeight - target.clientHeight;
		const user_has_scrolled_to_bottom = current_scroll_top >= max_scroll_top;
		if (user_has_scrolled_to_bottom) {
			user_has_scrolled_up = false;
		}
	}

	function handle_submit(): void {
		dispatch("submit");
	}

	async function resize(
		event: Event | { target: HTMLTextAreaElement | HTMLInputElement }
	): Promise<void> {
		await tick();
		if (lines === _max_lines) return;

		const target = event.target as HTMLTextAreaElement;
		const computed_styles = window.getComputedStyle(target);
		const padding_top = parseFloat(computed_styles.paddingTop);
		const padding_bottom = parseFloat(computed_styles.paddingBottom);
		const line_height = parseFloat(computed_styles.lineHeight);

		let max =
			_max_lines === undefined
				? false
				: padding_top + padding_bottom + line_height * _max_lines;
		let min = padding_top + padding_bottom + lines * line_height;

		target.style.height = "1px";

		let scroll_height;
		if (max && target.scrollHeight > max) {
			scroll_height = max;
		} else if (target.scrollHeight < min) {
			scroll_height = min;
		} else {
			scroll_height = target.scrollHeight;
		}

		target.style.height = `${scroll_height}px`;
	}

	function text_area_resize(
		_el: HTMLTextAreaElement,
		_value: string
	): any | undefined {
		if (lines === _max_lines) return;
		_el.style.overflowY = "scroll";
		_el.addEventListener("input", resize);

		if (!_value.trim()) return;
		resize({ target: _el });

		return {
			destroy: () => _el.removeEventListener("input", resize)
		};
	}

	type Line = {
		speaker: string;
		text: string;
	};

	let lines: Line[] = [];

	onMount(() => {
		if (lines.length === 0) {
			lines = [{ speaker: speakers[0] || '', text: '' }];
		}
	});

	function addLine(index: number) {
		lines = [
			...lines.slice(0, index + 1),
			{ speaker: speakers[0] || '', text: '' },
			...lines.slice(index + 1)
		];
	}

	function updateLineSpeaker(index: number, value: string) {
		lines[index].speaker = value;
		lines = [...lines];
	}

	function updateLineText(index: number, event: InputEvent) {
		const target = event.target as HTMLInputElement;
		lines[index].text = target.value;
		lines = [...lines];
	}

	let showPickerIndex: number | null = null;
	let pickerFilter = '';

	function handleKeyup(event: KeyboardEvent, idx: number) {
		const input = event.target as HTMLInputElement;
		const cursorPos = input.selectionStart || 0;
		const val = input.value;
		const lastColon = val.lastIndexOf(':', cursorPos - 1);
		if (lastColon >= 0) {
			pickerFilter = val.slice(lastColon + 1, cursorPos);
			showPickerIndex = idx;
		} else {
			showPickerIndex = null;
		}
	}

	function selectEmotion(emotion: string, idx: number) {
		const line = lines[idx];
		const input: HTMLInputElement = document.getElementById(`line-input-${idx}`) as HTMLInputElement;
		const cursorPos = input.selectionStart || 0;
		const text = line.text;
		const lastColon = text.lastIndexOf(':', cursorPos - 1);
		const before = text.slice(0, lastColon);
		const after = text.slice(cursorPos);
		line.text = `${before}:${emotion}:${after}`;
		lines = [...lines];
		showPickerIndex = null;
		const newPos = (before + `:${emotion}:`).length;
		setTimeout(() => {
			input.focus();
			input.setSelectionRange(newPos, newPos);
		}, 0);
	}
</script>

<div class="dialogue-container">
	<div class="dialogue-header">Dialogue</div>
	<div class="lines-container">
		{#each lines as line, idx}
			<div class="line">
				<select bind:value={line.speaker} on:change={(e) => updateLineSpeaker(idx, e.target.value)}>
					{#each speakers as sp}
						<option value={sp}>{sp}</option>
					{/each}
				</select>
				<div class="text-wrapper">
					<input
						id={`line-input-${idx}`}
						type="text"
						bind:value={line.text}
						placeholder="Type dialogue..."
						on:input={(e) => updateLineText(idx, e)}
						on:keyup={(e) => handleKeyup(e, idx)}
					/>
					{#if showPickerIndex === idx}
						<ul class="picker">
							{#each emotions.filter(em => em.toLowerCase().startsWith(pickerFilter.toLowerCase())) as em}
								<li on:click={() => selectEmotion(em, idx)}>{em}</li>
							{/each}
						</ul>
					{/if}
				</div>
				<button class="add-button" on:click={() => addLine(idx)}>+</button>
			</div>
		{/each}
	</div>
</div>

<style>
	.dialogue-container {
		border: 1px solid #000;
		border-radius: 5px;
		padding: 10px;
	}
	.dialogue-header {
		background: #4a90e2;
		color: #fff;
		padding: 10px;
		font-size: 1.2em;
		font-weight: bold;
		border-radius: 5px 5px 0 0;
	}
	.lines-container {
		margin-top: 10px;
	}
	.line {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}
	.line select {
		width: 100px;
		margin-right: 10px;
		background: #ffc600;
		font-weight: bold;
		border: 1px solid #000;
		border-radius: 3px;
	}
	.text-wrapper {
		position: relative;
		flex-grow: 1;
	}
	.text-wrapper input {
		width: 100%;
		padding: 5px;
		border: 1px solid #000;
		border-radius: 3px;
	}
	.picker {
		position: absolute;
		top: 100%;
		left: 0;
		background: #fff;
		border: 1px solid #000;
		border-radius: 3px;
		max-height: 100px;
		overflow-y: auto;
		list-style: none;
		margin: 2px 0 0;
		padding: 0;
		z-index: 10;
	}
	.picker li {
		padding: 5px;
		cursor: pointer;
	}
	.picker li:hover {
		background: #eee;
	}
	.add-button {
		margin-left: 10px;
		font-size: 1.5em;
		background: none;
		border: none;
		cursor: pointer;
	}
</style>
